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
# Increment this version (e.g., "v2.0" -> "v3.0") whenever you modify the prompt
# to automatically invalidate old cached summaries
PROMPT_VERSION = "v3.0"

# QUICK MODE PROMPT - Optimized for speed and conciseness
QUICK_SUMMARY_PROMPT_V3 = """
# ROLE & GOAL
You are a world-class summarization engine. Your goal is to create a concise, accurate, and insightful summary. Adhere to these principles:

# CORE PRINCIPLES

1. **BE DIRECT & CONCISE**
   - No filler words, no academic fluff, no unnecessary qualifiers.
   - Get straight to the point.
   - Example: Instead of "The speaker seems to suggest that perhaps one could consider...", write "The speaker argues that..."

2. **PRESERVE CONTEXT & ATTRIBUTION**
   - When the speaker quotes someone, you MUST attribute it clearly.
   - When referencing external sources (studies, books, people), maintain the connection to the main argument.
   - Examples:
     * "The speaker quotes Naval Ravikant: 'Specific knowledge is knowledge that you cannot be trained for.'"
     * "He references a Stanford study showing that..."

3. **FAITHFUL REPRESENTATION (NO SANITIZATION)**
   - Your PRIMARY job is to capture the speaker's actual message, tone, and intent.
   - Do NOT soften, sanitize, or filter the content, even if it is controversial or uses strong language.
   - Reflect the TRUTH of what was said, not a watered-down version.

4. **TONE MATCHING**
   - Match the speaker's tone (direct, provocative, academic, humorous, passionate, etc.).
   - If the speaker is fired up, your summary should convey that energy.

# JSON OUTPUT STRUCTURE (5 Components)

You MUST return a valid JSON object with the following structure:

{{
  "quick_takeaway": "A single, powerful sentence (max 150 characters) that captures the absolute core message.",
  "key_points": [
    "5-7 concise, scannable insights. Each should be a complete thought in 1-2 sentences."
  ],
  "topics": [
    {{"topic_name": "The first major theme or chapter", "summary_section_id": 1}},
    {{"topic_name": "The second major theme", "summary_section_id": 2}}
  ],
  "timestamps": [
    {{"time": "HH:MM:SS or MM:SS", "description": "Brief description of the key moment (max 100 chars)"}}
  ],
  "full_summary": [
    {{"id": 1, "content": "First paragraph of the detailed narrative summary..."}},
    {{"id": 2, "content": "Second paragraph..."}}
  ]
}}

# SPECIFIC INSTRUCTIONS

## quick_takeaway
- One sentence, maximum 150 characters.
- Must capture the speaker's MAIN point, not a generic description.

## key_points
- 5-7 points maximum.
- Each point is 1-2 sentences.
- Direct, actionable, specific.
- Preserve attribution.

## topics
- Identify 3-5 main sections/themes.
- The `summary_section_id` should correspond to the paragraph `id` in `full_summary`.

## timestamps
- Identify 3-5 key moments with exact timestamps (HH:MM:SS or MM:SS format).
- Brief description (max 100 characters).

## full_summary
- 5-8 well-developed paragraphs.
- Each paragraph is an object with a unique integer `id` and `content` (markdown text).
- Be concise but comprehensive.
- Preserve the speaker's actual message and tone.

# TRANSCRIPT
---
{transcript}
---

Video Title: {title}

# FINAL REMINDER
Return ONLY valid JSON. Do not include any explanatory text before or after the JSON object. Focus on essential insights only.
"""

# IN-DEPTH MODE PROMPT - Optimized for comprehensiveness and detail
INDEPTH_SUMMARY_PROMPT_V3 = """
# ROLE & GOAL
You are a world-class summarization engine. Your goal is to create a comprehensive, in-depth analysis of the provided video transcript. You must adhere to the following principles with absolute precision.

# CORE PRINCIPLES (NON-NEGOTIABLE)

1. **BE DIRECT & CONCISE**
   - No filler words, no academic fluff, no unnecessary qualifiers.
   - Get straight to the point.
   - Example: Instead of "The speaker seems to suggest that perhaps one could consider...", write "The speaker argues that..."

2. **PRESERVE CONTEXT & ATTRIBUTION**
   - When the speaker quotes someone, you MUST attribute it clearly.
   - When referencing external sources (studies, books, people), maintain the connection to the main argument.
   - Examples:
     * "The speaker quotes Naval Ravikant: 'Specific knowledge is knowledge that you cannot be trained for.'"
     * "He references a Stanford study showing that..."
     * "She cites her experience working at Google to illustrate..."

3. **FAITHFUL REPRESENTATION (NO SANITIZATION)**
   - Your PRIMARY job is to capture the speaker's actual message, tone, and intent.
   - Do NOT soften, sanitize, or filter the content, even if it is controversial or uses strong language.
   - If the speaker is direct or provocative, your summary must reflect that.
   - If the speaker uses strong language to make a point, preserve the strength of that language.
   - Reflect the TRUTH of what was said, not a watered-down version.

4. **TONE MATCHING**
   - Match the speaker's tone (direct, provocative, academic, humorous, passionate, etc.).
   - If the speaker is fired up, your summary should convey that energy.
   - If the speaker is analytical, your summary should be analytical.

# JSON OUTPUT STRUCTURE (8 Components - IN-DEPTH MODE)

You MUST return a valid JSON object with the following structure:

{{
  "quick_takeaway": "A single, powerful sentence (max 150 characters) that captures the absolute core message.",
  "key_points": [
    "10-15 detailed, comprehensive insights. Each should be a complete thought in 1-2 sentences."
  ],
  "topics": [
    {{"topic_name": "The first major theme or chapter", "summary_section_id": 1}},
    {{"topic_name": "The second major theme", "summary_section_id": 2}}
  ],
  "timestamps": [
    {{"time": "HH:MM:SS or MM:SS", "description": "Brief description of the key moment (max 100 chars)"}}
  ],
  "full_summary": [
    {{"id": 1, "content": "First paragraph of the detailed narrative summary..."}},
    {{"id": 2, "content": "Second paragraph..."}}
  ],
  "detailed_analysis": [
    {{"topic": "Topic name", "analysis": "Deep dive into this specific topic with nuanced insights, context, and implications."}}
  ],
  "key_quotes": [
    {{"quote": "Exact verbatim quote from the speaker or someone they reference", "context": "Brief context about when/why this was said", "speaker": "Who said it (the video speaker or someone they quoted)"}}
  ],
  "arguments": [
    {{"claim": "Main argument or claim made", "evidence": "Supporting evidence or reasoning provided", "counterpoint": "Any counterarguments or limitations mentioned (if applicable)"}}
  ]
}}

# SPECIFIC INSTRUCTIONS FOR EACH SECTION

## quick_takeaway
- One sentence, maximum 150 characters.
- Must capture the speaker's MAIN point, not a generic description.
- Be provocative if the speaker is provocative.

## key_points
- 10-15 points (comprehensive coverage).
- Each point is 1-2 sentences.
- Direct, actionable, specific.
- Preserve attribution (e.g., "The speaker quotes X..." or "He references Y...").
- Include nuanced details and context.

## topics
- Identify 5-8 main sections/themes (more granular than quick mode).
- The `summary_section_id` should correspond to the paragraph `id` in `full_summary` where that topic begins.

## timestamps
- Identify 5-8 key moments with exact timestamps (HH:MM:SS or MM:SS format).
- Brief description (max 100 characters).

## full_summary
- 8-12 comprehensive paragraphs (more detailed than quick mode).
- Each paragraph is an object with a unique integer `id` and `content` (markdown text).
- Be thorough and comprehensive.
- Preserve the speaker's actual message and tone.
- Maintain context and attribution throughout.
- Include important details, nuances, and implications.

## detailed_analysis (NEW - IN-DEPTH ONLY)
- 3-5 analysis objects, each focusing on a major topic or theme.
- Provide deeper insights, implications, and context for each topic.
- Go beyond surface-level summary to analyze WHY and HOW.

## key_quotes (NEW - IN-DEPTH ONLY)
- 3-5 important verbatim quotes.
- Include quotes from the speaker AND anyone they reference.
- Provide context for each quote (when/why it was said).
- Specify who said it (the speaker or someone they quoted).

## arguments (NEW - IN-DEPTH ONLY)
- 3-5 main arguments or claims made in the video.
- For each: state the claim, provide the evidence/reasoning, and note any counterpoints or limitations mentioned.
- Capture the logical structure of the speaker's argumentation.

# EXAMPLES (FEW-SHOT LEARNING)

## BAD EXAMPLE (What NOT to do):

{{
  "quick_takeaway": "The speaker discusses some interesting ideas about productivity.",
  "key_points": [
    "The speaker seems to suggest that perhaps one could consider the possibility of improving one's habits.",
    "There are various perspectives on time management that might be worth exploring."
  ],
  "full_summary": [
    {{"id": 1, "content": "In this video, the speaker talks about productivity and shares some thoughts on how people might be able to improve their daily routines. He mentions that there are different approaches to managing time, and some of these approaches could potentially be helpful for certain individuals in specific contexts."}}
  ]
}}

**Why this is bad:**
- Verbose and vague ("seems to suggest", "perhaps one could consider")
- No attribution or context
- Over-sanitized and generic
- Doesn't capture the speaker's actual message or tone

## GOOD EXAMPLE (What TO do):

{{
  "quick_takeaway": "Discipline is the path to freedom. You must control your time or it will control you.",
  "key_points": [
    "The speaker argues that discipline is not restrictive but liberating. He quotes Jocko Willink: 'Discipline equals freedom.'",
    "Most people fail because they lack systems, not motivation. Motivation is fleeting; systems are permanent.",
    "He references his experience as a Navy SEAL to illustrate that extreme ownership is the only path to success."
  ],
  "full_summary": [
    {{"id": 1, "content": "The speaker makes a provocative claim: discipline is the foundation of freedom. He quotes Jocko Willink, a former Navy SEAL, who says 'Discipline equals freedom.' This is not a metaphor. When you control your schedule, your habits, and your actions, you gain the freedom to pursue what matters. Without discipline, you are a slave to your impulses and distractions."}}
  ]
}}

**Why this is good:**
- Direct and concise
- Preserves attribution ("He quotes Jocko Willink...")
- Captures the speaker's provocative tone
- Specific and actionable

# TRANSCRIPT
---
{transcript}
---

Video Title: {title}

# FINAL REMINDER
Return ONLY valid JSON. Do not include any explanatory text before or after the JSON object. Adhere to the principles above with absolute precision.
"""

class AISummarizer:
    """
    AI-powered summarization service using OpenAI.
    
    Provides comprehensive summarization of video transcripts with intelligent
    handling of long content and detailed prompt engineering.
    """
    
    def __init__(self, cache_manager=None):
        """Initialize AI summarizer with cache manager and mode configurations."""
        self.cache = cache_manager

        # System prompt for consistent AI behavior - SIMPLE AND EFFECTIVE
        self.system_prompt = """You are a helpful assistant that summarizes video transcripts.
Always provide a summary of the transcript provided, regardless of length or content.
Format the summary with clear sections and markdown formatting."""

        # Mode-specific configurations for dual-mode summarization
        self.mode_configs = {
            "quick": {
                "prompt": QUICK_SUMMARY_PROMPT_V3,
                "chunking_threshold": 60,  # minutes
                "chunk_size": 3000,        # words (~20 min per chunk)
                "max_tokens": 2500
            },
            "indepth": {
                "prompt": INDEPTH_SUMMARY_PROMPT_V3,
                "chunking_threshold": 30,  # minutes
                "chunk_size": 1500,        # words (~10 min per chunk)
                "max_tokens": 8000
            }
        }

        logger.info("AISummarizer initialized with dual-mode support (quick/indepth)")
    
    def _estimate_duration_minutes(self, transcript: str) -> float:
        """
        Estimate video duration in minutes based on transcript word count.
        Assumes an average speaking rate of 150 words per minute.

        Args:
            transcript: Full video transcript text

        Returns:
            float: Estimated duration in minutes
        """
        word_count = len(transcript.split())
        return word_count / 150

    def generate_comprehensive_summary(self, transcript: str, title: str, mode: str = "quick") -> Dict:
        """
        Generate a comprehensive structured summary of a video transcript.
        Supports dual-mode summarization: "quick" (fast, concise) or "indepth" (comprehensive, detailed).
        Uses adaptive chunking for long videos based on mode-specific thresholds.

        Quick Mode (default):
        - 5 JSON components (quick_takeaway, key_points, topics, timestamps, full_summary)
        - Chunking threshold: 60 minutes
        - Max tokens: 2500
        - Optimized for speed and essential insights

        In-Depth Mode:
        - 8 JSON components (adds detailed_analysis, key_quotes, arguments)
        - Chunking threshold: 30 minutes
        - Max tokens: 8000
        - Optimized for comprehensive analysis and maximum detail

        Args:
            transcript: Full video transcript text
            title: Video title for additional context
            mode: Summarization mode - "quick" or "indepth" (default: "quick")

        Returns:
            dict: Structured summary with mode-specific components
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")

        # Validate and get mode configuration
        config = self.mode_configs.get(mode, self.mode_configs["quick"])
        if mode not in self.mode_configs:
            logger.warning(f"Invalid mode '{mode}', defaulting to 'quick'")
            mode = "quick"

        # Check cache first if available
        # Include PROMPT_VERSION and MODE in cache key to automatically invalidate old summaries
        if self.cache:
            versioned_content = PROMPT_VERSION + mode + transcript + title
            content_hash = self.cache.generate_content_hash(versioned_content)
            cached_summary = self.cache.get_cached_summary(content_hash)
            if cached_summary:
                logger.info(f"Retrieved {mode} summary from cache (version {PROMPT_VERSION}) for content hash: {content_hash}")
                # Ensure cached summary is dict (backward compatibility)
                if isinstance(cached_summary, str):
                    logger.warning("Cached summary is string format, converting to JSON structure")
                    return self._get_fallback_summary(transcript, title, cached_summary)
                return cached_summary
            else:
                logger.info(f"Cache miss for {mode} mode (version {PROMPT_VERSION}), will generate new summary")

        # Estimate video duration and choose appropriate strategy based on mode-specific threshold
        estimated_duration = self._estimate_duration_minutes(transcript)

        if estimated_duration > config["chunking_threshold"]:
            logger.info(f"Video duration estimated at {estimated_duration:.1f} minutes. Using adaptive chunking for {mode} mode (threshold: {config['chunking_threshold']} min).")
            summary_json = self._summarize_in_chunks(transcript, title, mode, config)
        else:
            logger.info(f"Video duration estimated at {estimated_duration:.1f} minutes. Using single-pass summarization for {mode} mode.")
            summary_json = self._summarize_single_pass(transcript, title, mode, config)

        # Cache the result if cache manager is available
        # Include mode in cache key for independent caching of quick vs indepth summaries
        if self.cache and summary_json:
            versioned_content = PROMPT_VERSION + mode + transcript + title
            content_hash = self.cache.generate_content_hash(versioned_content)
            self.cache.cache_summary(content_hash, summary_json)
            logger.info(f"Cached {mode} JSON summary (version {PROMPT_VERSION}) for content hash: {content_hash}")

        return summary_json

    def _summarize_single_pass(self, transcript: str, title: str, mode: str, config: dict) -> Dict:
        """
        Summarize a transcript in a single pass using mode-specific configuration.
        This is the standard method for videos below the mode's chunking threshold.

        Args:
            transcript: Full video transcript text
            title: Video title for context
            mode: Summarization mode ("quick" or "indepth")
            config: Mode-specific configuration dictionary

        Returns:
            dict: Structured JSON summary (5 components for quick, 8 for indepth)
        """
        try:
            # Use direct OpenAI API with mode-specific prompt and config
            logger.info(f"Using single-pass summarization for {mode} mode (version: {PROMPT_VERSION})")
            raw_response = self._generate_with_openai(transcript, title, mode, config)

            # Parse JSON response with comprehensive error handling
            try:
                summary_json = json.loads(raw_response)

                # Validate required fields (base fields for all modes)
                required_fields = ['quick_takeaway', 'key_points', 'topics', 'timestamps', 'full_summary']

                # Add in-depth specific fields for validation
                if mode == "indepth":
                    required_fields.extend(['detailed_analysis', 'key_quotes', 'arguments'])

                missing_fields = [field for field in required_fields if field not in summary_json]

                if missing_fields:
                    logger.error(f"CRITICAL: AI response missing required fields for {mode} mode: {missing_fields}")
                    logger.error(f"Raw AI Response (first 500 chars): {raw_response[:500]}")
                    return self._get_fallback_summary(transcript, title)

                # Validate data types
                if not isinstance(summary_json.get('key_points'), list):
                    logger.error("CRITICAL: 'key_points' is not a list")
                    return self._get_fallback_summary(transcript, title)

                if not isinstance(summary_json.get('full_summary'), list):
                    logger.error("CRITICAL: 'full_summary' is not a list")
                    return self._get_fallback_summary(transcript, title)

                logger.info(f"Successfully parsed {mode} JSON summary with {len(summary_json.get('full_summary', []))} paragraphs")
                return summary_json

            except json.JSONDecodeError as e:
                logger.error(f"CRITICAL: AI did not return valid JSON for {mode} mode. JSONDecodeError: {e}")
                logger.error(f"Raw AI Response (first 1000 chars): {raw_response[:1000]}")
                return self._get_fallback_summary(transcript, title)

        except Exception as e:
            logger.error(f"AI summarization failed for {mode} mode with exception: {e}", exc_info=True)
            return self._get_fallback_summary(transcript, title)

    def _summarize_in_chunks(self, transcript: str, title: str, mode: str, config: dict) -> Dict:
        """
        Summarize a long transcript by splitting it into chunks,
        summarizing each chunk, then creating a meta-summary.
        Uses mode-specific chunk size and configuration.

        Args:
            transcript: Full video transcript text
            title: Video title for context
            mode: Summarization mode ("quick" or "indepth")
            config: Mode-specific configuration dictionary

        Returns:
            dict: Structured JSON summary (5 components for quick, 8 for indepth)
        """
        try:
            # 1. Split transcript into chunks using mode-specific chunk size
            chunk_size = config["chunk_size"]
            chunks = self._split_transcript(transcript, chunk_size=chunk_size)
            logger.info(f"Split transcript into {len(chunks)} chunks for {mode} mode adaptive summarization (chunk size: {chunk_size} words)")

            # 2. Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                chunk_title = f"{title} (Part {i+1}/{len(chunks)})"
                logger.info(f"Summarizing chunk {i+1}/{len(chunks)} for {mode} mode")

                # Use a simplified prompt for chunk summarization
                chunk_summary = self._summarize_chunk(chunk, chunk_title)
                chunk_summaries.append(chunk_summary)

            # 3. Create meta-transcript from chunk summaries
            meta_transcript = "\n\n---\n\n".join(chunk_summaries)
            logger.info(f"Created meta-transcript from {len(chunk_summaries)} chunk summaries ({len(meta_transcript)} chars)")

            # 4. Summarize the meta-transcript to get final output using mode-specific config
            logger.info(f"Creating final {mode} summary from chunk summaries")
            final_summary = self._summarize_single_pass(meta_transcript, title, mode, config)

            return final_summary

        except Exception as e:
            logger.error(f"Error in chunked summarization for {mode} mode: {e}", exc_info=True)
            return self._get_fallback_summary(transcript, title)

    def _split_transcript(self, transcript: str, chunk_size: int) -> List[str]:
        """
        Split a transcript into chunks of approximately chunk_size words.

        Args:
            transcript: Full video transcript text
            chunk_size: Target number of words per chunk

        Returns:
            list: List of transcript chunks
        """
        words = transcript.split()
        chunks = [
            " ".join(words[i:i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]
        logger.info(f"Split {len(words)} words into {len(chunks)} chunks of ~{chunk_size} words each")
        return chunks

    def _summarize_chunk(self, chunk: str, chunk_title: str) -> str:
        """
        Summarize a single chunk of transcript.
        Returns a plain text summary (not JSON).

        Args:
            chunk: Transcript chunk to summarize
            chunk_title: Title for this chunk (includes part number)

        Returns:
            str: Plain text summary of the chunk
        """
        prompt = f"""
Summarize the following transcript segment. Be concise and capture the main points.

Transcript:
---
{chunk}
---

Title: {chunk_title}

Provide a 2-3 paragraph summary that captures the key information from this segment.
"""

        try:
            import requests

            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a concise summarization assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"OpenAI API error in chunk summarization: {response.status_code}")
                return chunk[:500] + "..."  # Fallback to truncated chunk

            result = response.json()
            chunk_summary = result["choices"][0]["message"]["content"].strip()
            logger.info(f"Generated chunk summary ({len(chunk_summary)} chars)")
            return chunk_summary

        except Exception as e:
            logger.error(f"Error summarizing chunk: {e}")
            return chunk[:500] + "..."  # Fallback to truncated chunk

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

    def _generate_with_openai(self, transcript: str, title: str, mode: str, config: dict) -> str:
        """
        Generate summary using OpenAI API directly with mode-specific configuration.

        Args:
            transcript: Full video transcript text
            title: Video title for context
            mode: Summarization mode ("quick" or "indepth")
            config: Mode-specific configuration dictionary

        Returns:
            str: Raw JSON string from AI (to be parsed by caller)
        """
        try:
            import requests

            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            # Increase transcript truncation length for comprehensive summaries
            max_length = 15000
            if len(transcript) > max_length:
                logger.warning(f"Transcript truncated from {len(transcript)} to {max_length} chars for {mode} mode")
                transcript = transcript[:max_length] + "..."

            # Use mode-specific prompt from config
            prompt_template = config["prompt"]
            prompt = prompt_template.format(title=title, transcript=transcript)

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Updated system prompt for JSON output
            json_system_prompt = """You are a helpful assistant that analyzes video transcripts and returns structured JSON summaries.
Always return valid JSON with no additional text before or after the JSON object.
Ensure all JSON is properly formatted and escaped."""

            # Use mode-specific temperature and max_tokens
            temperature = 0.3 if mode == "quick" else 0.5
            max_tokens = config["max_tokens"]

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": json_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            logger.info(f"Sending request to OpenAI API for {mode} mode (model: {payload['model']}, max_tokens: {max_tokens}, temp: {temperature})")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=90
            )

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"OpenAI API error for {mode} mode: {response.status_code} - {error_msg}")
                raise RuntimeError(f"OpenAI API error: {response.status_code}")

            result = response.json()
            raw_summary = result["choices"][0]["message"]["content"].strip()
            logger.info(f"Generated raw {mode} summary for '{title}' ({len(raw_summary)} chars)")
            return raw_summary

        except Exception as e:
            logger.error(f"OpenAI API call failed for {mode} mode: {e}")
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

