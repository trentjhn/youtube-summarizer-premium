# Implementation Guide: Long Video Support & Quality Improvements

## Overview

This guide provides complete implementation instructions for upgrading the YouTube Summarizer to handle long videos (30-60 minutes) effectively and dramatically improve summary quality by addressing verbosity, context loss, and over-sanitization.

---

## Changes Summary

| Component | Change | Complexity |
| :--- | :--- | :--- |
| **AI Prompt** | Complete rewrite with explicit quality rules | Medium |
| **Summarization Logic** | Add adaptive chunking for long videos | Medium |
| **Cache Versioning** | Increment to v3.0 | Low |
| **Testing** | Comprehensive quality validation | Medium |

---

## Phase 1: Update AI Prompt (Critical)

### 1.1. Create the New Prompt

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

**Action:** Replace the current `COMPREHENSIVE_SUMMARY_PROMPT` with this new version:

```python
COMPREHENSIVE_SUMMARY_PROMPT_V3 = """
# ROLE & GOAL
You are a world-class summarization engine. Your goal is to create a concise, accurate, and insightful summary of the provided video transcript. You must adhere to the following principles with absolute precision.

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

# JSON OUTPUT STRUCTURE

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

# SPECIFIC INSTRUCTIONS FOR EACH SECTION

## quick_takeaway
- One sentence, maximum 150 characters.
- Must capture the speaker's MAIN point, not a generic description.
- Be provocative if the speaker is provocative.

## key_points
- 5-7 points maximum.
- Each point is 1-2 sentences.
- Direct, actionable, specific.
- Preserve attribution (e.g., "The speaker quotes X..." or "He references Y...").

## topics
- Identify 3-5 main sections/themes.
- The `summary_section_id` should correspond to the paragraph `id` in `full_summary` where that topic begins.

## timestamps
- Identify 3-5 key moments with exact timestamps (HH:MM:SS or MM:SS format).
- Brief description (max 100 characters).

## full_summary
- 5-8 well-developed paragraphs.
- Each paragraph is an object with a unique integer `id` and `content` (markdown text).
- Be concise but comprehensive.
- Preserve the speaker's actual message and tone.
- Maintain context and attribution throughout.

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
```

### 1.2. Update the Prompt Version

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

**Action:** Increment the `PROMPT_VERSION` constant:

```python
PROMPT_VERSION = "v3.0"  # Changed from v2.0
```

This will invalidate old summaries and force regeneration with the new prompt.

---

## Phase 2: Implement Adaptive Summarization

### 2.1. Add Video Duration Detection

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

**Action:** Add a helper method to estimate video duration from transcript:

```python
def _estimate_duration_minutes(self, transcript: str) -> float:
    """
    Estimate video duration in minutes based on transcript word count.
    Assumes an average speaking rate of 150 words per minute.
    """
    word_count = len(transcript.split())
    return word_count / 150
```

### 2.2. Update `generate_summary` with Adaptive Logic

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

**Action:** Replace the existing `generate_summary` method with this version:

```python
def generate_summary(self, transcript: str, title: str) -> dict:
    """
    Generate a structured summary from a video transcript.
    Uses adaptive chunking for long videos (>45 minutes).
    
    Returns:
        dict: A structured summary with keys:
            - quick_takeaway (str)
            - key_points (list[str])
            - topics (list[dict])
            - timestamps (list[dict])
            - full_summary (list[dict])
    """
    # Estimate video duration
    estimated_duration = self._estimate_duration_minutes(transcript)
    
    MAX_DURATION_FOR_SINGLE_PASS = 45  # minutes
    
    if estimated_duration > MAX_DURATION_FOR_SINGLE_PASS:
        logger.info(f"Video duration estimated at {estimated_duration:.1f} minutes. Using adaptive chunking.")
        return self._summarize_in_chunks(transcript, title)
    else:
        logger.info(f"Video duration estimated at {estimated_duration:.1f} minutes. Using single-pass summarization.")
        return self._summarize_single_pass(transcript, title)
```

### 2.3. Implement Single-Pass Summarization

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

**Action:** Create the `_summarize_single_pass` method (this is your existing logic with the new prompt):

```python
def _summarize_single_pass(self, transcript: str, title: str) -> dict:
    """
    Summarize a transcript in a single pass.
    """
    try:
        # Format the prompt with the transcript and title
        prompt = COMPREHENSIVE_SUMMARY_PROMPT_V3.format(
            transcript=transcript,
            title=title
        )
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a world-class summarization engine."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.4
        )
        
        summary_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            summary_json = json.loads(summary_text)
            
            # Validate required fields
            required_fields = ['quick_takeaway', 'key_points', 'topics', 'timestamps', 'full_summary']
            for field in required_fields:
                if field not in summary_json:
                    logger.error(f"Missing required field in AI response: {field}")
                    return self._get_fallback_summary(transcript, title)
            
            return summary_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {summary_text[:500]}")
            return self._get_fallback_summary(transcript, title)
            
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return self._get_fallback_summary(transcript, title)
```

### 2.4. Implement Chunking Summarization

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

**Action:** Create the `_summarize_in_chunks` method:

```python
def _summarize_in_chunks(self, transcript: str, title: str) -> dict:
    """
    Summarize a long transcript by splitting it into chunks,
    summarizing each chunk, then creating a meta-summary.
    """
    try:
        # 1. Split transcript into chunks (2250 words per chunk = ~15 minutes)
        chunks = self._split_transcript(transcript, chunk_size=2250)
        logger.info(f"Split transcript into {len(chunks)} chunks")
        
        # 2. Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            chunk_title = f"{title} (Part {i+1}/{len(chunks)})"
            logger.info(f"Summarizing chunk {i+1}/{len(chunks)}")
            
            # Use a simplified prompt for chunk summarization
            chunk_summary = self._summarize_chunk(chunk, chunk_title)
            chunk_summaries.append(chunk_summary)
        
        # 3. Create meta-transcript from chunk summaries
        meta_transcript = "\n\n---\n\n".join(chunk_summaries)
        
        # 4. Summarize the meta-transcript to get final output
        logger.info("Creating final summary from chunk summaries")
        final_summary = self._summarize_single_pass(meta_transcript, title)
        
        return final_summary
        
    except Exception as e:
        logger.error(f"Error in chunked summarization: {e}")
        return self._get_fallback_summary(transcript, title)

def _split_transcript(self, transcript: str, chunk_size: int) -> list:
    """
    Split a transcript into chunks of approximately chunk_size words.
    """
    words = transcript.split()
    return [
        " ".join(words[i:i + chunk_size]) 
        for i in range(0, len(words), chunk_size)
    ]

def _summarize_chunk(self, chunk: str, chunk_title: str) -> str:
    """
    Summarize a single chunk of transcript.
    Returns a plain text summary (not JSON).
    """
    prompt = f"""
Summarize the following transcript segment. Be concise and capture the main points.

Transcript:
---
{chunk}
---

Title: {chunk_title}

Provide a 2-3 paragraph summary.
"""
    
    try:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error summarizing chunk: {e}")
        return chunk[:500] + "..."  # Fallback to truncated chunk
```

---

## Phase 3: Testing & Validation

### 3.1. Test Cases

You MUST test with these specific video types:

| Test # | Video Type | Duration | Expected Behavior |
| :--- | :--- | :--- | :--- |
| **1** | Long lecture/podcast | 60 min | Adaptive chunking triggered, coherent summary |
| **2** | Short news clip | 10 min | Single-pass, concise summary |
| **3** | Controversial commentary | Any | Strong language preserved, no sanitization |
| **4** | Complex argument with quotes | Any | Quotes attributed correctly, context maintained |
| **5** | Humorous content | Any | Tone matched, humor preserved |

### 3.2. Quality Checklist

For each test video, verify:

- [ ] **Conciseness:** No filler words or verbose language
- [ ] **Attribution:** Quotes and references are clearly attributed
- [ ] **Faithful representation:** Speaker's actual message is captured
- [ ] **Tone matching:** Summary reflects the speaker's tone
- [ ] **Structure:** All 5 JSON fields are present and valid
- [ ] **Coherence:** Summary is easy to read and understand

### 3.3. Performance Monitoring

Track these metrics:

- **Processing time:** Should be <30s for short videos, <60s for long videos
- **Token usage:** Monitor cost per video
- **Error rate:** Should be <5% (fallback summaries)

---

## Phase 4: Rollout Strategy

### 4.1. Incremental Deployment

1. **Deploy backend changes** with the new prompt and adaptive logic
2. **Increment `PROMPT_VERSION` to v3.0** to invalidate old summaries
3. **Test with 5-10 diverse videos** to validate quality
4. **Monitor error logs** for any JSON parsing failures
5. **Iterate on prompt** if quality is not satisfactory

### 4.2. Rollback Plan

If the new prompt produces worse results:

1. **Revert `PROMPT_VERSION` to v2.0**
2. **Revert the prompt** to the previous version
3. **Keep the adaptive chunking logic** (it's still valuable)

---

## Expected Outcomes

After implementation, you should see:

✅ **Long videos (30-60 min):** High-quality summaries with preserved detail  
✅ **Concise summaries:** No verbose language, direct and to the point  
✅ **Context preservation:** Quotes and references properly attributed  
✅ **Faithful representation:** Speaker's actual message captured  
✅ **Tone matching:** Summary reflects the speaker's style  

---

## Cost Impact

**Current cost per video:**
- 30-min video: ~$0.01
- 60-min video: ~$0.015

**New cost with chunking:**
- 30-min video: ~$0.01 (no change, single-pass)
- 60-min video: ~$0.025 (67% increase, but still very cheap)

**Conclusion:** The quality improvement is worth the minimal cost increase.

---

## Next Steps

1. Provide this guide to your AI coding assistant
2. Have them implement all changes
3. Test thoroughly with diverse videos
4. Iterate on the prompt based on results
5. Enjoy dramatically improved summary quality!
