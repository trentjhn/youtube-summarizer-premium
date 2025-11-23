"""
AI Summarizer - LangChain-based summarization service

This module provides AI-powered summarization of YouTube video transcripts using
LangChain and OpenAI's GPT models. Implements sophisticated prompt engineering
and handles long-form content through map-reduce patterns.
"""

import os
import json
import logging
from typing import Optional, List, Dict

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain.chains.summarize import load_summarize_chain
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available - install with: pip install langchain langchain-openai")

# Configure logging
logger = logging.getLogger(__name__)

# Prompt version for cache invalidation
# Increment this version (e.g., "v2.0" -> "v2.1") whenever you modify the prompt
# to automatically invalidate old cached summaries
PROMPT_VERSION = "v2.0"

# JSON-structured prompt for premium UI with interactive digest
COMPREHENSIVE_SUMMARY_PROMPT = """
Analyze the following video transcript and generate a structured JSON output.

**Your Goal:** Create a comprehensive, multi-faceted summary that is both scannable and allows for deep, interactive reading.

**JSON Output Structure:**
{{
  "quick_takeaway": "A single, powerful sentence that captures the absolute core message of the video.",
  "key_points": [
    "A list of 5-7 of the most important, scannable takeaways as concise sentences."
  ],
  "topics": [
    {{"topic_name": "The first major theme or chapter of the video", "summary_section_id": 1}},
    {{"topic_name": "The second major theme or chapter", "summary_section_id": 2}}
  ],
  "timestamps": [
    {{"time": "HH:MM:SS", "description": "A brief description of the key moment at this timestamp."}}
  ],
  "full_summary": [
    {{"id": 1, "content": "First paragraph of the detailed narrative summary..."}},
    {{"id": 2, "content": "Second paragraph of the detailed narrative summary..."}}
  ]
}}

**Instructions:**
1.  **`quick_takeaway`**: Must be a single, compelling sentence (max 150 characters).
2.  **`key_points`**: Extract 5-7 of the most critical insights. Do not just repeat sentences from the summary.
3.  **`topics`**: Identify 3-5 main sections/themes of the video. The `summary_section_id` should correspond to the paragraph `id` in the `full_summary` where that topic begins.
4.  **`timestamps`**: Identify 3-5 key moments with their exact timestamp (format: HH:MM:SS or MM:SS) and a brief description (max 100 characters).
5.  **`full_summary`**: This is the most important part. Write a detailed, flowing narrative in 5-8 well-developed paragraphs. Each paragraph is an object with a unique integer `id` and `content` (the paragraph text in markdown format).

**Important:** Return ONLY valid JSON. Do not include any explanatory text before or after the JSON object.

Video Title: {title}

Transcript:
{transcript}
"""

class AISummarizer:
    """
    AI-powered summarization service using OpenAI.
    
    Provides comprehensive summarization of video transcripts with intelligent
    handling of long content and detailed prompt engineering.
    """
    
    def __init__(self, cache_manager=None):
        """Initialize AI summarizer with cache manager."""
        self.cache = cache_manager

        # System prompt for consistent AI behavior - SIMPLE AND EFFECTIVE
        self.system_prompt = """You are a helpful assistant that summarizes video transcripts.
Always provide a summary of the transcript provided, regardless of length or content.
Format the summary with clear sections and markdown formatting."""

        logger.info("AISummarizer initialized")
    
    def generate_comprehensive_summary(self, transcript: str, title: str) -> Dict:
        """
        Generate a comprehensive structured summary of a video transcript.

        Uses OpenAI API to generate JSON-structured summaries with multiple components:
        - quick_takeaway: Single sentence core message
        - key_points: List of 5-7 critical insights
        - topics: Main themes with section IDs
        - timestamps: Key moments with time codes
        - full_summary: Detailed narrative paragraphs

        Args:
            transcript: Full video transcript text
            title: Video title for additional context

        Returns:
            dict: Structured summary with all components (see _get_fallback_summary for schema)
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")

        # Check cache first if available
        # Include PROMPT_VERSION in cache key to automatically invalidate old summaries
        if self.cache:
            versioned_content = PROMPT_VERSION + transcript + title
            content_hash = self.cache.generate_content_hash(versioned_content)
            cached_summary = self.cache.get_cached_summary(content_hash)
            if cached_summary:
                logger.info(f"Retrieved summary from cache (version {PROMPT_VERSION}) for content hash: {content_hash}")
                # Ensure cached summary is dict (backward compatibility)
                if isinstance(cached_summary, str):
                    logger.warning("Cached summary is string format, converting to JSON structure")
                    return self._get_fallback_summary(transcript, title, cached_summary)
                return cached_summary
            else:
                logger.info(f"Cache miss for version {PROMPT_VERSION}, will generate new summary")

        try:
            # Use direct OpenAI API (more reliable than LangChain)
            logger.info(f"Using direct OpenAI API for JSON-structured summarization (prompt version: {PROMPT_VERSION})")
            raw_response = self._generate_with_openai(transcript, title)

            # Parse JSON response with comprehensive error handling
            try:
                summary_json = json.loads(raw_response)

                # Validate required fields
                required_fields = ['quick_takeaway', 'key_points', 'topics', 'timestamps', 'full_summary']
                missing_fields = [field for field in required_fields if field not in summary_json]

                if missing_fields:
                    logger.error(f"CRITICAL: AI response missing required fields: {missing_fields}")
                    logger.error(f"Raw AI Response (first 500 chars): {raw_response[:500]}")
                    return self._get_fallback_summary(transcript, title)

                # Validate data types
                if not isinstance(summary_json.get('key_points'), list):
                    logger.error("CRITICAL: 'key_points' is not a list")
                    return self._get_fallback_summary(transcript, title)

                if not isinstance(summary_json.get('full_summary'), list):
                    logger.error("CRITICAL: 'full_summary' is not a list")
                    return self._get_fallback_summary(transcript, title)

                logger.info(f"Successfully parsed JSON summary with {len(summary_json.get('full_summary', []))} paragraphs")

                # Cache the result if cache manager is available
                if self.cache:
                    versioned_content = PROMPT_VERSION + transcript + title
                    content_hash = self.cache.generate_content_hash(versioned_content)
                    self.cache.cache_summary(content_hash, summary_json)
                    logger.info(f"Cached JSON summary (version {PROMPT_VERSION}) for content hash: {content_hash}")

                return summary_json

            except json.JSONDecodeError as e:
                logger.error(f"CRITICAL: AI did not return valid JSON. JSONDecodeError: {e}")
                logger.error(f"Raw AI Response (first 1000 chars): {raw_response[:1000]}")
                return self._get_fallback_summary(transcript, title)

        except Exception as e:
            logger.error(f"AI summarization failed with exception: {e}", exc_info=True)
            return self._get_fallback_summary(transcript, title)
    
    def _generate_with_langchain(self, transcript: str, title: str) -> str:
        """
        Generate summary using LangChain with map-reduce pattern.

        This method handles long transcripts by:
        1. Splitting transcript into manageable chunks
        2. Summarizing each chunk (map phase)
        3. Combining summaries into final summary (reduce phase)

        Args:
            transcript: Full video transcript text
            title: Video title for context

        Returns:
            str: Comprehensive summary
        """
        try:
            # Initialize LLM
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,
                api_key=api_key
            )

            # Define prompts for map-reduce
            map_prompt = PromptTemplate(
                input_variables=["text"],
                template="""
Summarize this section of a video transcript. Include the main topics, key information, and any specific details mentioned.

Section:
{text}

SUMMARY:
"""
            )

            combine_prompt = PromptTemplate(
                input_variables=["text"],
                template=f"""
Create a comprehensive summary from these section summaries of a video titled "{title}".
Combine all key information, remove redundancies, and organize logically.

Summaries to combine:
{{text}}

COMPREHENSIVE SUMMARY:
"""
            )

            # Split transcript into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )

            chunks = text_splitter.split_text(transcript)
            docs = [Document(page_content=chunk) for chunk in chunks]

            logger.info(f"Split transcript into {len(docs)} chunks for processing")

            # Use appropriate chain based on document count
            if len(docs) > 1:
                # Map-reduce for multiple chunks
                chain = load_summarize_chain(
                    llm,
                    chain_type="map_reduce",
                    map_prompt=map_prompt,
                    combine_prompt=combine_prompt,
                    verbose=False
                )
            else:
                # Simple chain for single chunk
                chain = load_summarize_chain(
                    llm,
                    chain_type="stuff",
                    prompt=combine_prompt,
                    verbose=False
                )

            # Generate summary
            summary = chain.invoke({"input_documents": docs})

            # Extract text from response
            if isinstance(summary, dict):
                summary_text = summary.get("output_text", str(summary))
            else:
                summary_text = str(summary)

            logger.info(f"Generated summary using LangChain for '{title}'")
            return summary_text

        except Exception as e:
            logger.error(f"LangChain summarization failed: {e}")
            raise RuntimeError(f"LangChain summarization failed: {e}")

    def _generate_with_openai(self, transcript: str, title: str) -> str:
        """
        Generate summary using OpenAI API directly.

        Returns raw JSON string from AI (to be parsed by caller).
        """
        try:
            import requests

            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            # Increase transcript truncation length for comprehensive summaries
            max_length = 15000
            if len(transcript) > max_length:
                logger.warning(f"Transcript truncated from {len(transcript)} to {max_length} chars")
                transcript = transcript[:max_length] + "..."

            # Use the new JSON-structured prompt
            prompt = COMPREHENSIVE_SUMMARY_PROMPT.format(title=title, transcript=transcript)

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Updated system prompt for JSON output
            json_system_prompt = """You are a helpful assistant that analyzes video transcripts and returns structured JSON summaries.
Always return valid JSON with no additional text before or after the JSON object.
Ensure all JSON is properly formatted and escaped."""

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": json_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 4000
            }

            logger.info(f"Sending request to OpenAI API with model: {payload['model']}")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=90
            )

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"OpenAI API error: {response.status_code} - {error_msg}")
                raise RuntimeError(f"OpenAI API error: {response.status_code}")

            result = response.json()
            raw_summary = result["choices"][0]["message"]["content"].strip()
            logger.info(f"Generated raw summary for '{title}' ({len(raw_summary)} chars)")
            return raw_summary

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise RuntimeError(f"OpenAI API call failed: {e}")
    

    def _get_fallback_summary(self, transcript: str, title: str, existing_summary: str = None) -> Dict:
        """
        Generate a basic fallback summary when JSON parsing fails or for backward compatibility.

        This method ensures the system never crashes due to AI response errors.
        It creates a minimal but valid JSON structure that the frontend can render.

        Args:
            transcript: The video transcript
            title: The video title
            existing_summary: Optional existing text summary to convert to JSON format

        Returns:
            dict: A valid JSON summary structure with minimal content
        """
        logger.warning(f"Using fallback summary for video: {title}")

        # If we have an existing text summary, use it; otherwise create from transcript
        if existing_summary:
            summary_content = existing_summary
        else:
            # Create a simple summary from the first 2000 characters of transcript
            words = transcript.split()[:300]  # ~300 words = ~2000 chars
            summary_content = ' '.join(words)
            if len(transcript.split()) > 300:
                summary_content += "... (summary truncated due to processing error)"

        # Return a minimal but valid JSON structure
        fallback_structure = {
            "quick_takeaway": f"Summary of: {title}",
            "key_points": [
                "This is a fallback summary generated due to an unexpected error.",
                "The full transcript is available below.",
                "Please try regenerating the summary for better results."
            ],
            "topics": [
                {"topic_name": "Video Content", "summary_section_id": 1}
            ],
            "timestamps": [],
            "full_summary": [
                {
                    "id": 1,
                    "content": summary_content
                }
            ]
        }

        logger.info("Fallback summary structure created successfully")
        return fallback_structure

