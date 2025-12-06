# Tone and Style Preference: Design and Integration

## 1. Prompt Optimization Strategy

The tone preference will be implemented as a **dynamic variable** injected into the existing prompt templates (`QUICK_SUMMARY_PROMPT_V3` and `INDEPTH_SUMMARY_PROMPT_V3`).

### 1.1. Backend Logic (`ai_summarizer.py`)

The `generate_summary` function will accept a `tone` parameter (defaulting to 'Objective').

```python
# In ai_summarizer.py

# Default Tone
DEFAULT_TONE = "Objective (Faithful Representation)"

# Update mode_configs to include a tone placeholder in the prompt
# This is a conceptual change; the actual prompt string will be formatted later

def generate_summary(self, transcript: str, title: str, mode: str = "quick", tone: str = DEFAULT_TONE) -> dict:
    # ...
    
    # Select the base prompt
    base_prompt = config["prompt"]
    
    # Inject the tone into the prompt template
    final_prompt = base_prompt.format(
        transcript=transcript, 
        title=title, 
        tone=tone # New injection point
    )
    
    # ... rest of the summarization logic using final_prompt
```

### 1.2. Prompt Template Update

The prompt template itself needs a new section to guide the AI's output style.

**New Prompt Section (Added to both Quick and In-Depth Prompts):**

```
# TONE AND STYLE CONSTRAINT
The final summary MUST be written in a {tone} tone. 
- If the tone is 'Academic', use formal language, complex sentence structures, and cite concepts.
- If the tone is 'Casual', use conversational language, contractions, and simple vocabulary.
- If the tone is 'Skeptical', critically evaluate the speaker's claims, highlight assumptions, and use cautious language.
- If the tone is 'Provocative', use strong, challenging language and emphasize controversial points.
- If the tone is 'Objective (Faithful Representation)', strictly adhere to the speaker's original tone and intent without adding external bias.
```

### 1.3. Predefined Tone Options

The frontend will offer the following options:

| Tone Option | Description | Rationale |
| :--- | :--- | :--- |
| **Objective** (Default) | Strictly adheres to the speaker's original tone and intent. | The safest, most faithful representation. |
| **Academic** | Formal, structured, uses precise terminology. | For technical papers, lectures, or deep dives. |
| **Casual** | Conversational, easy-to-read, friendly. | For quick, light reviews of content. |
| **Skeptical** | Critically evaluates claims, highlights assumptions and biases. | For critical analysis of persuasive content. |
| **Provocative** | Uses strong, challenging language, emphasizes controversial points. | For generating debate points or strong opinions. |

## 2. UX Integration: Unified Control Panel

The Tone Preference feature will be integrated into the **Unified Personalization Control Panel** (Feature 2) alongside the Mode and Timestamp selectors.

### 2.1. API Design Update

The `/api/process-video` endpoint will now accept three optional parameters:

```
POST /api/process-video
Body: { 
  "url": "...",
  "mode": "quick" | "indepth",  // Default: "quick"
  "start_time": "MM:SS",        // Optional
  "end_time": "MM:SS",          // Optional
  "tone": "Objective" | "Academic" | "Casual" | "Skeptical" | "Provocative" // Default: "Objective"
}
```

### 2.2. Caching Strategy Update

The cache key must be updated to include the new `tone` parameter.

**New Cache Key Structure:**

```python
cache_key = f"{video_id}_{mode}_{start_time}_{end_time}_{tone}_{PROMPT_VERSION}"
```

**Guardrail:** If any of the optional parameters (`start_time`, `end_time`, `tone`) are not provided, the backend will use the default values ("00:00", "end", "Objective") when constructing the cache key. This ensures consistency.

### 2.3. Frontend Component (`PersonalizationControlPanel.jsx`)

The Control Panel will have three distinct sections:

1.  **Summarization Mode:** (Radio buttons/cards for Quick/In-Depth)
2.  **Video Segment:** (Input fields for Start/End Time)
3.  **Output Tone:** (Dropdown or Radio buttons for Tone Selection)

This design ensures that the complexity is managed, and the user has full control over the output.
