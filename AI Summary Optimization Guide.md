# AI Summary Optimization Guide

**Objective:** This guide provides the exact code changes needed to transform the AI summary output from a multi-section, condensed format to a single, comprehensive, and descriptive narrative summary. This will align the output with your goal of gaining the same knowledge as if you watched the entire video.

## 1. Analysis of the Current State

- **Video:** "How To Escape The Poverty Mindset" (36 minutes)
- **Current Summary:** Multi-section format (Executive Summary, Key Takeaways, etc.) with a "Detailed Analysis" of only 3 paragraphs.
- **Assessment:** The current summary is too brief for a 36-minute video and lacks the depth, context, and specific examples required to be a true substitute for watching the video.

## 2. Implementation: Code Changes

Here are the specific changes to be made in `youtube-summarizer/src/services/ai_summarizer.py`.

### Step 1: Replace the Prompt

First, replace the existing `COMPREHENSIVE_SUMMARY_PROMPT` with the new, improved version designed for a single, narrative summary.

**Find and replace this entire block of code:**

```python
# In ai_summarizer.py, around line 28

# Comprehensive summary prompt for high-quality structured summaries
COMPREHENSIVE_SUMMARY_PROMPT = '''You are an expert analyst tasked with creating a comprehensive, structured summary of a video transcript. Your goal is to produce a summary so insightful that a person can gain the same core knowledge as if they watched the entire video.

Analyze the following transcript and generate these distinct sections:

1.  **Executive Summary:** A concise, 1-3 sentence paragraph that captures the absolute essence of the video. What is the main point or conclusion?

2.  **Key Takeaways:** A bulleted list of the 5-7 most important points, findings, or actionable insights from the video. Each bullet point should be clear and self-contained.

3.  **Detailed Analysis:** A more in-depth exploration of the main topics discussed. This section should elaborate on the key takeaways, providing context, evidence, or arguments presented in the video. Use 2-4 paragraphs.

4.  **Noteworthy Quotes:** A list of 2-3 impactful or memorable quotes from the video that capture a key sentiment or piece of evidence. Attribute the quote if the speaker is identifiable.

Format the entire output in Markdown with clear headers for each section.

Video Title: {title}

Transcript:
"""
{transcript}
"""
'''
```

**With this new prompt:**

```python
# In ai_summarizer.py, replace the old prompt

# New prompt for a comprehensive, single-narrative summary
COMPREHENSIVE_NARRATIVE_SUMMARY_PROMPT = '''You are an expert analyst creating a comprehensive narrative summary of a video transcript. Your goal is to produce a summary so detailed and insightful that someone reading it gains the same knowledge and understanding as if they watched the entire video.

Write a flowing, well-structured narrative summary that:
- Captures ALL major arguments, concepts, and examples presented.
- Explains the context and reasoning behind each key point.
- Includes specific details, analogies, and scenarios mentioned.
- Explores the implications and practical applications of the ideas.
- Maintains a logical flow from one concept to the next.
- Uses 5-8 well-developed paragraphs (or more for longer videos).

Do NOT use section headers or bullet points. Write in complete, flowing paragraphs that read like a comprehensive article. Focus on depth and insight, not brevity.

Video Title: {title}

Transcript:
"""
{transcript}
"""

Write a comprehensive narrative summary:
'''
```

### Step 2: Update the `_generate_with_openai` Method

Next, update the `_generate_with_openai` method to use the new prompt and adjust the parameters for a longer, more detailed output.

**Find and replace the entire `_generate_with_openai` method with this updated version:**

```python
# In ai_summarizer.py, replace the entire method

def _generate_with_openai(self, transcript: str, title: str) -> str:
    """Generate summary using OpenAI API directly."""
    try:
        import requests

        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # --- PARAMETER CHANGE 1: Increase transcript truncation length ---
        max_length = 15000  # Increased from 12000 to capture more of long videos
        if len(transcript) > max_length:
            logger.warning(f"DEBUG: Transcript truncated from {len(transcript)} to {max_length} chars")
            transcript = transcript[:max_length] + "..."

        # --- PROMPT CHANGE: Use the new narrative prompt ---
        prompt = COMPREHENSIVE_NARRATIVE_SUMMARY_PROMPT.format(title=title, transcript=transcript)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            # --- PARAMETER CHANGE 2: Adjust temperature for more natural prose ---
            "temperature": 0.4,  # Increased from 0.3
            # --- PARAMETER CHANGE 3: Increase max_tokens for longer summaries ---
            "max_tokens": 4000  # Increased from 3000
        }

        logger.info(f"DEBUG: Sending request to OpenAI API with model: {payload['model']}")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90  # Increased timeout for longer generation
        )

        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"OpenAI API error: {response.status_code} - {error_msg}")
            raise RuntimeError(f"OpenAI API error: {response.status_code}")

        result = response.json()
        summary = result["choices"][0]["message"]["content"]
        logger.info(f"Generated summary for '{title}' ({len(transcript)} chars)")
        return summary

    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise RuntimeError(f"OpenAI API call failed: {e}")
```

## 3. Explanation of Changes

### Prompt Change:
- **Why:** The new prompt explicitly instructs the AI to create a single, flowing narrative. It removes the multi-section requirement and instead focuses on depth, context, and including specific examples. This directly addresses your request for a more comprehensive, article-style summary.

### Parameter Adjustments:
- **`max_length = 15000`**: This increases the amount of the transcript that is sent to the AI. For a 36-minute video, this allows the model to see more of the content, leading to a more complete summary.
- **`temperature = 0.4`**: A slight increase from `0.3` encourages the model to produce slightly more creative and natural-sounding prose, which is ideal for a narrative summary. It's still low enough to prevent the AI from making things up.
- **`max_tokens = 4000`**: This is the most critical change. It increases the maximum length of the generated summary from ~2250 words to ~3000 words, giving the AI the space it needs to write the detailed, multi-paragraph summary you want.
- **`timeout = 90`**: Increased to give the API more time to generate the longer summary, preventing potential timeout errors.

## 4. How to Test the Improvement

1.  **Apply the code changes** to your `ai_summarizer.py` file.
2.  **Restart your application.**
3.  **Reprocess the same video:** `https://www.youtube.com/watch?v=1ET-_h_y8Ek`
4.  **Compare the new output** to the previous version. You should see:
    - A single "Full Summary" section.
    - A significantly longer and more detailed summary (likely 3-4 times longer).
    - Inclusion of concepts like the "Pavlov's dog" analogy, the importance of maintenance, and the distinction between looking rich and being rich.

This implementation will produce a summary that is far more aligned with your goal of a true video-watching substitute.
