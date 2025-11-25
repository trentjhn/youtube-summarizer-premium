# Improved Summarization Strategy: Long Videos & High Quality

## 1. Core Problem

Your current system struggles with:
- **Long videos (30-60 min):** Quality degrades, context is lost.
- **Summary quality:** Too verbose, loses context, over-sanitizes.

## 2. The Solution: Two-Pronged Approach

### Prong 1: Advanced Prompt Engineering (Immediate)

We will replace the current AI prompt with a **highly engineered, multi-part prompt** that gives the AI specific instructions on how to behave.

**New Prompt Structure:**

1.  **Role & Goal:** "You are a world-class summarization engine. Your goal is to create a concise, accurate, and insightful summary..."
2.  **Key Principles (The Fixes):**
    -   **Conciseness:** "Be direct. No filler words. Get to the point."
    -   **Context Preservation:** "When the speaker quotes someone, attribute it clearly (e.g., \"The speaker quotes John Doe as saying...\")."
    -   **Faithful Representation:** "Capture the speaker's actual message, including strong language or controversial points. Do not soften or sanitize the content."
    -   **Tone Matching:** "Match the speaker's tone (e.g., direct, provocative, academic, humorous)."
3.  **JSON Structure:** The same 5-part JSON structure you currently use.
4.  **Examples (Few-Shot Learning):**
    -   **Bad Example:** Show the AI what a verbose, sanitized summary looks like.
    -   **Good Example:** Show the AI a concise, accurate summary that preserves context.
5.  **The Transcript:** The video transcript.

**Why this works:** By providing explicit instructions and examples, we force the AI to abandon its default "safe" behavior and adopt the style you want.

### Prong 2: Adaptive Summarization (For Long Videos)

For videos longer than 45 minutes, a single pass is not enough. We will implement an **adaptive chunking and hierarchical summarization** strategy.

**How it works:**

```
IF video_duration > 45 minutes:
  1. Split transcript into 15-minute chunks
  2. Summarize each chunk individually (get 3-4 chunk summaries)
  3. Combine chunk summaries into a "meta-transcript"
  4. Summarize the meta-transcript to get the final output
ELSE:
  1. Summarize the full transcript in one pass (current method)
```

**Why this works:**
-   **Preserves detail:** Each chunk gets full attention.
-   **Maintains context:** The meta-summary connects the chunks.
-   **Avoids token limits:** Never exceeds the model's capacity.
-   **Cost-effective:** Only used when necessary.

## 3. Implementation Details

### 3.1. New AI Prompt

```python
# In ai_summarizer.py

COMPREHENSIVE_SUMMARY_PROMPT_V3 = """
# ROLE & GOAL
You are a world-class summarization engine. Your goal is to create a concise, accurate, and insightful summary of the provided video transcript. You must adhere to the following principles:

# PRINCIPLES
1.  **Be Direct & Concise:** Do not use filler words or academic language. Get straight to the point.
2.  **Preserve Context:** When the speaker quotes someone or references an external source, you MUST attribute it clearly. For example: "The speaker references a study from Stanford..." or "He quotes Naval Ravikant as saying..."
3.  **Faithful Representation:** Your primary job is to capture the speaker's actual message, tone, and intent. Do NOT soften, sanitize, or filter the content, even if it is controversial or uses strong language. Reflect the truth of what was said.
4.  **Tone Matching:** Match the speaker's tone (e.g., direct, provocative, academic, humorous, etc.).

# JSON OUTPUT STRUCTURE
(Your existing 5-part JSON structure here)

# EXAMPLES (FEW-SHOT LEARNING)

## Bad Example (What NOT to do):
- Verbose, over-sanitized, loses context
- "The speaker seems to suggest that perhaps one could consider the possibility of..."

## Good Example (What TO do):
- Direct, concise, preserves context
- "The speaker argues that you must take action now. He quotes a Navy SEAL: 'Discipline equals freedom.'"

# TRANSCRIPT
---
{transcript}
---

Video Title: {title}
"""
```

### 3.2. Adaptive Chunking Logic

```python
# In ai_summarizer.py

def generate_summary(self, transcript: str, title: str) -> dict:
    # Estimate video duration (150 words per minute)
    word_count = len(transcript.split())
    estimated_duration_minutes = word_count / 150

    MAX_DURATION_FOR_SINGLE_PASS = 45

    if estimated_duration_minutes > MAX_DURATION_FOR_SINGLE_PASS:
        # Use adaptive chunking for long videos
        return self._summarize_in_chunks(transcript, title)
    else:
        # Use single-pass summarization for shorter videos
        return self._summarize_single_pass(transcript, title)

def _summarize_single_pass(self, transcript: str, title: str) -> dict:
    # Your existing summarization logic with the new prompt
    # ...

def _summarize_in_chunks(self, transcript: str, title: str) -> dict:
    # 1. Split transcript into chunks (e.g., 2250 words per chunk for 15 min)
    chunks = self._split_transcript(transcript, chunk_size=2250)
    
    # 2. Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_title = f"{title} (Part {i+1}/{len(chunks)})"
        # Use a simpler prompt for chunk summarization
        summary = self._summarize_single_pass(chunk, chunk_title)
        chunk_summaries.append(summary["full_summary"][0]["content"])
    
    # 3. Create meta-transcript
    meta_transcript = "\n\n---\n\n".join(chunk_summaries)
    
    # 4. Summarize the meta-transcript
    final_summary = self._summarize_single_pass(meta_transcript, title)
    return final_summary

def _split_transcript(self, transcript: str, chunk_size: int) -> list[str]:
    words = transcript.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
```

## 4. Model Recommendation

**Start with:** GPT-4o-mini (your current model)

**If quality is still not sufficient, upgrade to:**
- **Gemini 2.5 Flash:** Excellent at following complex instructions, great value.
- **GPT-4o:** The gold standard for nuance and reasoning, but more expensive.

## 5. Testing Strategy

To verify these changes, you must test with a diverse set of videos:

| Test Case | Video Type | Expected Outcome |
| :--- | :--- | :--- |
| **1. Long Video** | 60-minute lecture | Adaptive chunking is triggered, summary is coherent and detailed. |
| **2. Short Video** | 10-minute news clip | Single-pass summarization is used, summary is concise. |
| **3. Controversial Topic** | A direct, provocative commentary | Summary captures the strong language and main point without sanitization. |
| **4. Complex Argument** | A video with multiple quotes and data | Summary correctly attributes quotes and maintains the main argument. |
| **5. Humorous Content** | A comedy sketch or review | Summary reflects the humorous tone. |

## 6. Implementation Plan

1.  **Update `ai_summarizer.py`** with the new `COMPREHENSIVE_SUMMARY_PROMPT_V3`.
2.  **Implement the adaptive logic** in `generate_summary` to choose between single-pass and chunking.
3.  **Add the `_summarize_in_chunks` and `_split_transcript` methods**.
4.  **Update `PROMPT_VERSION`** in your cache versioning system to `v3.0` to invalidate old summaries.
5.  **Run the testing suite** with the 5 video types listed above.
6.  **Analyze the results** and iterate on the prompt if necessary.

This two-pronged approach will solve both your long-video and summary quality problems, making your tool significantly more effective and valuable.
