"""
Transcript Extractor - YouTube transcript extraction service

This module handles extracting transcripts from YouTube videos using multiple
fallback methods to ensure high success rates. Implements caching to avoid
repeated API calls and provides robust error handling.

Extraction Methods (in priority order):
1. YouTube Transcript API - Primary method using official captions
2. Web scraping - Fallback for videos with disabled API access
3. Browser automation - Last resort for complex cases

Key Features:
- Multiple URL format support (youtube.com, youtu.be, embed URLs)
- Automatic language detection and fallback
- Caching integration for performance
- Comprehensive error handling and logging
- Title extraction from multiple sources
"""

import re
import logging
import requests
import os
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

# YouTube Transcript API for primary extraction method
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    logging.warning("youtube_transcript_api not available - install with: pip install youtube-transcript-api")

# Selenium for browser automation fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("selenium not available - install with: pip install selenium")

# yt-dlp for robust transcript extraction
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logging.warning("yt-dlp not available - install with: pip install yt-dlp")

# Configure logging
logger = logging.getLogger(__name__)

class TranscriptExtractor:
    """
    YouTube transcript extraction service with multiple fallback methods.
    
    Provides robust transcript extraction using a hierarchy of methods,
    from fast API calls to slower but more reliable browser automation.
    Integrates with cache manager for performance optimization.
    
    Args:
        cache_manager: Cache manager instance for storing/retrieving transcripts
    """
    
    def __init__(self, cache_manager):
        """
        Initialize transcript extractor with cache manager.
        
        Args:
            cache_manager: CacheManager instance for performance optimization
        """
        self.cache = cache_manager
        
        # User agent for web scraping (appears as regular browser)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        logger.info(f"TranscriptExtractor initialized - yt-dlp: {YT_DLP_AVAILABLE}, API: {TRANSCRIPT_API_AVAILABLE}, Selenium: {SELENIUM_AVAILABLE}")
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract YouTube video ID from various URL formats.
        
        Supports multiple YouTube URL formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/watch?v=VIDEO_ID&t=123s (with timestamp)
        - https://m.youtube.com/watch?v=VIDEO_ID (mobile)
        
        Args:
            url: YouTube video URL in any supported format
            
        Returns:
            str: YouTube video ID (11 characters)
            
        Raises:
            ValueError: If URL format is not recognized or video ID cannot be extracted
        """
        # Clean the URL and handle common variations
        url = url.strip()
        
        # List of regex patterns for different YouTube URL formats
        patterns = [
            # Standard watch URLs: youtube.com/watch?v=VIDEO_ID
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            
            # Short URLs: youtu.be/VIDEO_ID
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            
            # Embed URLs: youtube.com/embed/VIDEO_ID
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            
            # Mobile URLs: m.youtube.com/watch?v=VIDEO_ID
            r'(?:m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            
            # Handle URLs with additional parameters
            r'(?:youtube\.com\/watch\?.*v=)([a-zA-Z0-9_-]{11})',
        ]
        
        # Try each pattern until we find a match
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info(f"Extracted video ID: {video_id} from URL: {url}")
                return video_id
        
        # If no pattern matches, try parsing as URL parameters
        try:
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    if len(video_id) == 11:  # YouTube video IDs are always 11 characters
                        logger.info(f"Extracted video ID from URL params: {video_id}")
                        return video_id
        except Exception as e:
            logger.warning(f"Error parsing URL parameters: {e}")
        
        # If all methods fail, raise an error
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_transcript(self, video_id: str) -> Dict[str, Any]:
        """
        Get transcript using multiple fallback methods with caching.

        Attempts transcript extraction in order of reliability and speed:
        1. Check cache first (fastest)
        2. yt-dlp (NEW PRIMARY - most reliable and actively maintained)
        3. YouTube Transcript API (fallback)
        4. Browser automation (last resort)

        Args:
            video_id: YouTube video ID

        Returns:
            dict: Transcript data with keys:
                - transcript: Full transcript text
                - title: Video title
                - method: Extraction method used
                - language: Detected language code

        Raises:
            Exception: If all extraction methods fail
        """
        # Check cache first for performance
        cached_data = self.cache.get_cached_transcript(video_id)
        if cached_data:
            logger.info(f"Retrieved transcript for {video_id} from cache")
            return cached_data

        transcript_data = None
        last_error = None

        # Method 1: yt-dlp (NEW PRIMARY METHOD - most reliable)
        if YT_DLP_AVAILABLE:
            try:
                logger.info(f"Attempting transcript extraction for {video_id} using yt-dlp...")
                transcript_data = self._extract_with_ytdlp(video_id)
                logger.info(f"Successfully extracted transcript for {video_id} using yt-dlp")
            except Exception as e:
                logger.warning(f"yt-dlp extraction failed for {video_id}: {e}")
                last_error = e

        # Method 2: YouTube Transcript API (fallback)
        if not transcript_data and TRANSCRIPT_API_AVAILABLE:
            try:
                logger.info(f"Attempting transcript extraction for {video_id} using API...")
                transcript_data = self._extract_with_api(video_id)
                logger.info(f"Successfully extracted transcript for {video_id} using API")
            except Exception as e:
                logger.warning(f"API extraction failed for {video_id}: {e}")
                last_error = e

        # Method 3: Browser automation (last resort)
        if not transcript_data and SELENIUM_AVAILABLE:
            try:
                logger.info(f"Attempting transcript extraction for {video_id} using browser automation...")
                transcript_data = self._extract_with_browser(video_id)
                logger.info(f"Successfully extracted transcript for {video_id} using browser automation")
            except Exception as e:
                logger.warning(f"Browser automation failed for {video_id}: {e}")
                last_error = e

        # If all methods failed, raise the last error
        if not transcript_data:
            error_msg = f"All transcript extraction methods failed for video {video_id}"
            if last_error:
                error_msg += f". Last error: {last_error}"
            raise Exception(error_msg)

        # Cache the successful result
        self.cache.cache_transcript(video_id, transcript_data)

        return transcript_data
    
    def _extract_with_api(self, video_id: str) -> Dict[str, Any]:
        """
        Extract transcript using YouTube Transcript API.
        
        Primary extraction method using the official YouTube transcript API.
        Handles multiple languages and automatic caption detection.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            dict: Transcript data with API method tag
            
        Raises:
            Exception: If API extraction fails
        """
        try:
            # youtube-transcript-api v1.x requires instantiation
            # (Changed from static methods in v0.x)
            ytt_api = YouTubeTranscriptApi()

            # Get available transcript languages
            transcript_list = ytt_api.list(video_id)

            # Try to get English transcript first, then any available language
            transcript = None
            language_code = 'en'

            try:
                # Prefer manually created transcripts over auto-generated
                transcript = transcript_list.find_manually_created_transcript(['en'])
                language_code = 'en'
            except:
                try:
                    # Fall back to auto-generated English
                    transcript = transcript_list.find_generated_transcript(['en'])
                    language_code = 'en'
                except:
                    # Use any available transcript
                    for available_transcript in transcript_list:
                        transcript = available_transcript
                        language_code = transcript.language_code
                        break

            if not transcript:
                raise Exception("No transcripts available")

            # Fetch the actual transcript data
            transcript_data = transcript.fetch()

            # Preserve raw transcript data with timestamps for Phase 4 slicing feature
            # Format: [{"start": 0.0, "duration": 3.5, "text": "..."}, ...]
            # Note: v1.x returns FetchedTranscriptSnippet objects with .text, .start, .duration attributes
            raw_transcript_segments = [
                {"start": entry.start, "duration": entry.duration, "text": entry.text}
                for entry in transcript_data
            ]

            # Combine all transcript segments into single text
            # Note: v1.x uses .text attribute instead of ['text'] dict access
            transcript_text = ' '.join([entry.text for entry in transcript_data])

            # Clean up the transcript text
            transcript_text = self._clean_transcript_text(transcript_text)

            # Get video title
            title = self._get_video_title(video_id)

            return {
                'transcript': transcript_text,
                'raw_segments': raw_transcript_segments,  # Preserve timestamp data
                'title': title,
                'method': 'youtube_api',
                'language': language_code,
                'is_auto_generated': transcript.is_generated
            }

        except Exception as e:
            raise Exception(f"YouTube API extraction failed: {e}")

    def _extract_with_ytdlp(self, video_id: str) -> Dict[str, Any]:
        """
        Extract transcript using yt-dlp library.

        Primary extraction method using yt-dlp, a robust and actively maintained
        tool for extracting YouTube content including subtitles and transcripts.

        Args:
            video_id: YouTube video ID

        Returns:
            dict: Transcript data with yt-dlp method tag

        Raises:
            Exception: If yt-dlp extraction fails
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        # Use a temporary file path for the subtitle
        temp_subtitle_path_template = f"/tmp/{video_id}"

        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
            'outtmpl': temp_subtitle_path_template,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', f'Video {video_id}')

                # Determine the path of the downloaded VTT file
                subtitle_path = f"/tmp/{video_id}.en.vtt"
                if not os.path.exists(subtitle_path):
                    # If the file wasn't pre-downloaded, trigger download
                    ydl.download([url])
                    if not os.path.exists(subtitle_path):
                        raise FileNotFoundError(f"VTT file not found for {video_id} after download attempt.")

                # Parse the VTT file
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    transcript_parts = []
                    for line in lines:
                        line = line.strip()
                        # Skip empty lines, timestamps, metadata, and VTT headers
                        if (line and
                            '-->' not in line and
                            not line.isdigit() and
                            'WEBVTT' not in line and
                            'Kind:' not in line and
                            'Language:' not in line and
                            not line.startswith('<')):
                            # Remove VTT timestamp tags like <00:00:00.480>
                            import re
                            clean_line = re.sub(r'<[\d:.]+>', '', line)
                            clean_line = re.sub(r'<c>', '', clean_line)
                            clean_line = re.sub(r'</c>', '', clean_line)
                            if clean_line.strip():
                                transcript_parts.append(clean_line.strip())

                transcript = ' '.join(transcript_parts)

                # Clean up the temporary file
                if os.path.exists(subtitle_path):
                    os.remove(subtitle_path)

                if len(transcript) < 150:
                    raise ValueError(f"Transcript is too short ({len(transcript)} chars). Content may be insufficient for a quality summary.")

                return {
                    'transcript': transcript,
                    'raw_segments': [],  # TODO: Parse VTT timestamps for Phase 4 slicing
                    'title': title,
                    'method': 'yt-dlp',
                    'language': 'en'
                }

        except Exception as e:
            logger.error(f"[yt-dlp] Extraction failed for {video_id}: {e}")
            raise Exception(f"yt-dlp extraction failed: {e}")

    def _extract_with_scraping(self, video_id: str) -> Dict[str, Any]:
        """
        Extract transcript using web scraping.
        
        Fallback method that scrapes YouTube's web interface for transcript data.
        Less reliable than API but works for some videos where API fails.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            dict: Transcript data with scraping method tag
            
        Raises:
            Exception: If web scraping fails
        """
        try:
            # Construct YouTube URL
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Make request to YouTube page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title from page
            title_element = soup.find('meta', property='og:title')
            title = title_element['content'] if title_element else f"Video {video_id}"
            
            # Look for transcript data in page scripts
            # This is a simplified implementation - real scraping would be more complex
            transcript_text = "Web scraping transcript extraction not fully implemented"
            
            return {
                'transcript': transcript_text,
                'title': title,
                'method': 'web_scraping',
                'language': 'unknown'
            }
            
        except Exception as e:
            raise Exception(f"Web scraping extraction failed: {e}")
    
    def _extract_with_browser(self, video_id: str) -> Dict[str, Any]:
        """
        Extract transcript using browser automation.

        Last resort method using Selenium to automate a real browser.
        Can handle complex cases but is slow and resource-intensive.

        Args:
            video_id: YouTube video ID

        Returns:
            dict: Transcript data with browser automation method tag

        Raises:
            Exception: If browser automation fails
        """
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium not available for browser automation")

        driver = None
        try:
            # Configure Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")  # Required for some environments
            chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
            chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
            chrome_options.add_argument(f"--user-agent={self.headers['User-Agent']}")

            # Initialize Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)

            # Navigate to YouTube video
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Opening YouTube video in browser: {url}")
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "title"))
            )

            # Extract title
            title = driver.title.replace(" - YouTube", "")
            logger.info(f"Extracted title: {title}")

            # Try to find and click transcript button
            transcript_text = self._extract_transcript_from_page(driver, video_id)

            return {
                'transcript': transcript_text,
                'title': title,
                'method': 'browser_automation',
                'language': 'unknown'
            }

        except Exception as e:
            logger.error(f"Browser automation extraction failed: {e}")
            raise Exception(f"Browser automation extraction failed: {e}")

        finally:
            # Always clean up browser resources
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")

    def _extract_transcript_from_page(self, driver, video_id: str) -> str:
        """
        Extract transcript text from YouTube page using browser automation.

        Attempts to:
        1. Find and click the transcript button
        2. Wait for transcript panel to load
        3. Extract all transcript text
        4. Handle pagination if needed

        Args:
            driver: Selenium WebDriver instance
            video_id: YouTube video ID (for logging)

        Returns:
            str: Extracted transcript text

        Raises:
            Exception: If transcript cannot be extracted
        """
        try:
            # Wait for video to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )

            # Try to find transcript button (may have different selectors)
            transcript_button_selectors = [
                "button[aria-label*='Show transcript']",
                "button[aria-label*='transcript']",
                "yt-button-shape[aria-label*='transcript']",
                "button:contains('Transcript')"
            ]

            transcript_button = None
            for selector in transcript_button_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        transcript_button = elements[0]
                        break
                except:
                    continue

            if not transcript_button:
                # Try finding by partial text match
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    aria_label = button.get_attribute("aria-label")
                    if aria_label and "transcript" in aria_label.lower():
                        transcript_button = button
                        break

            if transcript_button:
                logger.info("Found transcript button, clicking...")
                transcript_button.click()

                # Wait for transcript panel to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-transcript-segment-list-renderer"))
                )

            # Extract transcript segments
            transcript_segments = []
            try:
                # Find all transcript segments
                segments = driver.find_elements(By.CSS_SELECTOR, "ytd-transcript-segment-list-renderer yt-formatted-string")

                for segment in segments:
                    text = segment.get_text().strip()
                    if text:
                        transcript_segments.append(text)

                if transcript_segments:
                    transcript_text = " ".join(transcript_segments)
                    logger.info(f"Extracted {len(transcript_segments)} transcript segments")
                    return transcript_text
                else:
                    raise Exception("No transcript segments found")

            except Exception as e:
                logger.warning(f"Could not extract transcript segments: {e}")
                # Try alternative extraction method
                return self._extract_transcript_from_html(driver)

        except Exception as e:
            logger.error(f"Transcript extraction from page failed: {e}")
            raise Exception(f"Could not extract transcript from page: {e}")

    def _extract_transcript_from_html(self, driver) -> str:
        """
        Fallback method to extract transcript from page HTML.

        Searches for transcript data in page source or JavaScript variables.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            str: Extracted transcript text or error message
        """
        try:
            page_source = driver.page_source

            # Look for transcript data in JavaScript
            if "transcriptSegmentListRenderer" in page_source:
                logger.info("Found transcript data in page source")
                # Extract text between common patterns
                import re
                # This is a simplified extraction - real implementation would parse JSON
                matches = re.findall(r'"text":"([^"]+)"', page_source)
                if matches:
                    return " ".join(matches)

            raise Exception("Could not find transcript data in page source")

        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            raise Exception(f"Could not extract transcript from HTML: {e}")
    
    def _get_video_title(self, video_id: str) -> str:
        """
        Extract video title from YouTube metadata.
        
        Uses web scraping to get video title from YouTube's page metadata.
        Fallback method when title is not available from transcript API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            str: Video title or fallback if extraction fails
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple methods to extract title
            title_sources = [
                soup.find('meta', property='og:title'),
                soup.find('meta', attrs={'name': 'title'}),
                soup.find('title')
            ]
            
            for source in title_sources:
                if source:
                    title = source.get('content') or source.get_text()
                    if title:
                        # Clean up YouTube title formatting
                        title = title.replace(' - YouTube', '').strip()
                        return title
            
            # Fallback if no title found
            return f"Video {video_id}"
            
        except Exception as e:
            logger.warning(f"Failed to extract title for {video_id}: {e}")
            return f"Video {video_id}"
    
    def _clean_transcript_text(self, text: str) -> str:
        """
        Clean and normalize transcript text.
        
        Removes artifacts from automatic transcription and normalizes
        whitespace for better AI processing.
        
        Args:
            text: Raw transcript text
            
        Returns:
            str: Cleaned transcript text
        """
        if not text:
            return ""
        
        # Remove common transcript artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
        text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = text.strip()
        
        return text

