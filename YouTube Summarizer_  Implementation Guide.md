# YouTube Summarizer: `yt-dlp` Implementation Guide

**Objective:** This document provides a comprehensive, step-by-step guide for an AI coding assistant to replace the current broken transcript extraction mechanism with the recommended `yt-dlp` solution.

## 1. Current System State & Problem

- **The Goal:** The YouTube Summarizer application is designed to take a YouTube URL, extract the video transcript, and generate a summary using the OpenAI API.
- **The Problem:** The core function, **transcript extraction**, is completely non-functional. All three of the system’s built-in methods have failed:
    1.  **YouTube Transcript API:** Blocked by YouTube.
    2.  **Web Scraping:** Never fully implemented; returns placeholder text.
    3.  **Browser Automation:** Uses outdated UI selectors and no longer works.
- **The Impact:** The system cannot obtain video transcripts, and therefore cannot generate summaries. The application is currently **non-functional**.

## 2. The Solution: Implement `yt-dlp`

We will integrate the `yt-dlp` library, a well-maintained and robust tool for interacting with YouTube. This will become the new **primary method** for transcript extraction due to its high reliability and ability to adapt to YouTube’s changes.

### Why `yt-dlp`?

- **Reliability:** Actively maintained by a large community, ensuring it stays current with YouTube’s infrastructure.
- **Cost-Effective:** It is a free and open-source solution.
- **Low Maintenance:** It abstracts away the complexity of interacting with YouTube, reducing future maintenance overhead.
- **Effectiveness:** It is highly effective at downloading video metadata, including subtitles and auto-generated captions.

## 3. Step-by-Step Implementation Plan

### Step 1: Install Dependencies

First, add the `yt-dlp` library to the project's Python environment and ensure all system-level dependencies are met.

1.  **Install the Python package:**

    ```bash
    pip install yt-dlp
    ```

2.  **Update `requirements.txt`:** Add the following line to your `requirements.txt` file to ensure the dependency is tracked for future deployments.

    ```
    yt-dlp>=2023.10.13
    ```

3.  **Ensure `ffmpeg` is installed:** `yt-dlp` sometimes relies on `ffmpeg` for processing media. Ensure it is installed in the development and production environments.

    ```bash
    # For Debian/Ubuntu-based systems
    sudo apt-get update && sudo apt-get install -y ffmpeg
    ```

### Step 2: Implement the `yt-dlp` Extraction Method

Next, you will modify the `TranscriptExtractor` service to include a new method for fetching transcripts using `yt-dlp`.

**File to Edit:** `src/services/transcript_extractor.py`

1.  **Import necessary libraries** at the top of the file.

    ```python
    import yt_dlp
    import requests
    from logging import getLogger

    logger = getLogger(__name__)
    ```

2.  **Add the new private method** `_extract_with_ytdlp` to the `TranscriptExtractor` class. This method will contain all the logic for interacting with `yt-dlp`.

    ```python
    def _extract_with_ytdlp(self, video_id: str) -> dict:
        """Extracts a transcript using the yt-dlp library."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
            'outtmpl': f'/tmp/{video_id}', # Ensure unique output file
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', f'Video {video_id}')

                # yt-dlp provides the path to the downloaded subtitle file
                requested_subs = info.get('requested_subtitles')
                if not requested_subs or 'en' not in requested_subs:
                    raise FileNotFoundError("English subtitles not found.")

                subtitle_path = requested_subs['en'].get('filepath')
                if not subtitle_path or not os.path.exists(subtitle_path):
                    # If filepath is not available, download it
                    ydl.download([url])
                    subtitle_path = f"/tmp/{video_id}.en.vtt"
                    if not os.path.exists(subtitle_path):
                         raise FileNotFoundError("Could not download VTT file.")

                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    # Simple VTT parsing: ignore metadata and join text lines
                    lines = f.readlines()
                    transcript_lines = []
                    for line in lines:
                        if '-->' not in line and not line.strip().isdigit() and line.strip() != 'WEBVTT':
                            transcript_lines.append(line.strip())
                
                # Clean up the downloaded file
                os.remove(subtitle_path)

                transcript = ' '.join(transcript_lines)

                if len(transcript) < 100: # Basic validation
                    raise ValueError(f"Transcript is too short ({len(transcript)} chars). It might be empty.")

                return {
                    'transcript': transcript,
                    'title': title,
                    'method': 'yt-dlp',
                }
        except Exception as e:
            logger.error(f"[yt-dlp] Extraction failed for {video_id}: {e}")
            raise
    ```

### Step 3: Update the Main `get_transcript` Method

Now, modify the primary `get_transcript` method to use your new `_extract_with_ytdlp` method as the **first choice**.

**File to Edit:** `src/services/transcript_extractor.py`

```python
# Inside the TranscriptExtractor class

def get_transcript(self, video_id: str) -> dict:
    """Extracts transcript using a fallback chain of methods."""
    # Check cache first (existing logic)
    cached_data = self.cache_manager.get(f"transcript:{video_id}")
    if cached_data:
        logger.info(f"Cache hit for {video_id}")
        return cached_data

    last_error = None

    # === METHOD 1: yt-dlp (NEW PRIMARY) ===
    try:
        logger.info(f"Attempting transcript extraction for {video_id} using yt-dlp...")
        transcript_data = self._extract_with_ytdlp(video_id)
        self.cache_manager.set(f"transcript:{video_id}", transcript_data)
        return transcript_data
    except Exception as e:
        logger.warning(f"yt-dlp method failed for {video_id}: {e}")
        last_error = e

    # === METHOD 2: YouTube Transcript API (FALLBACK) ===
    try:
        logger.info(f"Attempting transcript extraction for {video_id} using API...")
        transcript_data = self._extract_with_api(video_id)
        self.cache_manager.set(f"transcript:{video_id}", transcript_data)
        return transcript_data
    except Exception as e:
        logger.warning(f"API method failed for {video_id}: {e}")
        last_error = e

    # === METHOD 3: Browser Automation (LAST RESORT) ===
    try:
        logger.info(f"Attempting transcript extraction for {video_id} using browser...")
        transcript_data = self._extract_with_browser(video_id)
        self.cache_manager.set(f"transcript:{video_id}", transcript_data)
        return transcript_data
    except Exception as e:
        logger.error(f"Browser method failed for {video_id}: {e}")
        last_error = e

    # If all methods fail, raise an exception
    raise Exception(f"All transcript extraction methods failed for {video_id}. Last error: {last_error}")

```

**Note:** The placeholder-based web scraping method has been removed from the chain as it was not functional.

## 4. Testing Strategy

To ensure the fix is working correctly, follow this testing protocol.

### Step 1: Unit Testing

Create a standalone test script (`test_ytdlp.py`) to isolate and test the new extraction method.

```python
# test_ytdlp.py
import sys
sys.path.insert(0, 'src')

from services.transcript_extractor import TranscriptExtractor
from services.cache_manager import CacheManager

if __name__ == "__main__":
    # Use a dummy cache manager that does nothing
    cache_manager = CacheManager(redis_client=None)
    extractor = TranscriptExtractor(cache_manager)

    test_videos = [
        "m92GE57Rn7o",  # A video known to have a transcript
        "jNQXAC9IVRw",  # "Me at the zoo" - short, should work
        "dQw4w9WgXcQ",  # A music video, may or may not have a transcript
    ]

    for video_id in test_videos:
        print(f"\n--- Testing video: {video_id} ---")
        try:
            result = extractor.get_transcript(video_id)
            print(f"  ✅ Success! Method: {result['method']}")
            print(f"  Title: {result['title']}")
            print(f"  Transcript Length: {len(result['transcript'])} characters")
            print(f"  Transcript Preview: {result['transcript'][:100]}...")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
```

Run the test script from your terminal:

```bash
python3 test_ytdlp.py
```

### Step 2: End-to-End Testing

1.  **Clear the Database:** Ensure you are testing fresh by clearing any previously cached (and failed) entries.

    ```bash
    # Run this in your terminal
    python3 -c "import sqlite3; conn = sqlite3.connect('src/database/app.db'); conn.execute('DELETE FROM videos'); conn.commit(); print('Database cleared.')"
    ```

2.  **Run the Application:** Start the Flask backend server.

    ```bash
    python3 src/main.py
    ```

3.  **Send a Test Request:** Use `curl` or a REST client to send a request to the API endpoint.

    ```bash
    curl -X POST http://127.0.0.1:5001/api/process-video \
    -H "Content-Type: application/json" \
    -d '{"video_url": "https://www.youtube.com/watch?v=m92GE57Rn7o"}'
    ```

4.  **Verify the Output:** Check the API response and the backend logs to confirm that a valid summary was generated and that the `yt-dlp` method was used.

## 5. Success Criteria

The implementation will be considered a success when the following criteria are met:

-   The system successfully extracts transcripts for over 95% of videos that have them.
-   The `transcript` field in the database contains the full text, not a placeholder.
-   The final AI-generated summary is specific and directly related to the video's content.
-   The backend logs clearly show that the `yt-dlp` method is being used successfully.

## 6. Future Optimizations

After this critical fix is deployed, consider the following improvements:

-   **Asynchronous Processing:** Move the entire `get_transcript` and `summarize` flow into a background task queue (e.g., Celery) to prevent blocking API requests.
-   **Improved Error Handling:** Create more specific exceptions for different failure modes (e.g., `TranscriptNotFound`, `ExtractionFailed`).
-   **Database Migration:** Plan a migration from SQLite to a more robust database like PostgreSQL to support future scaling.

This guide provides all the necessary information to resolve the critical issue. Proceed with the implementation as outlined steps to restore the application to a fully functional state.
