# Final Consolidated Implementation Guide: Personalization Suite Upgrade

This guide consolidates all planned features—**Timestamp-Based Summarization**, **Tone and Style Preference**, and the **Unified Control Panel**—into a single, actionable roadmap for the coding assistant.

## Executive Summary

The goal is to implement a **Personalization Suite** that allows users to control the content (via timestamps) and the style (via tone preference) of the summary output. This upgrade is designed to be **incremental, safe, and fully backward-compatible**.

## 1. Updated Implementation Roadmap

The features are bundled to maximize efficiency, as both Timestamp and Tone require similar changes to the API and Caching logic.

| Phase | Feature | Focus | Technical Changes |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Backend Core Logic** | **Optimization & Personalization** | Update API to accept `start`/`end`/`tone`. Implement `_slice_transcript`. Update Caching logic to include all three parameters. Inject `tone` into prompts. |
| **Phase 2** | **Frontend Integration** | **UX Consolidation** | Create `PersonalizationControlPanel.jsx`. Integrate Mode, Timestamp, and Tone selectors into the new component. |
| **Phase 3** | **Monetization Strategy** | **Future Infrastructure** | Deferred. (Cost estimation logic is noted but not implemented). |

## 2. Phase 1: Backend Core Logic (API, Caching, Slicing, Tone)

### 2.1. API Update (`main.py`)

The `/api/process-video` endpoint must be updated to accept three new optional parameters.

```python
# In main.py (Conceptual change)
@app.route("/api/process-video", methods=["POST"])
def process_video():
    # ...
    data = request.get_json()
    url = data.get("url")
    mode = data.get("mode", "quick")
    
    # NEW OPTIONAL PARAMETERS
    start_time = data.get("start_time", "00:00")
    end_time = data.get("end_time", "end")
    tone = data.get("tone", "Objective")
    
    # ... pass these to the summarizer service
```

### 2.2. Caching Update (`CacheManager` / `ai_summarizer.py`)

The cache key must be updated to include all personalization parameters.

```python
# In CacheManager or ai_summarizer.py (Conceptual change)
def generate_cache_key(video_id, mode, start_time, end_time, tone):
    # Use a standardized format for time (e.g., convert MM:SS to seconds)
    # The PROMPT_VERSION is already included in the mode_configs logic
    return f"{video_id}_{mode}_{start_time}_{end_time}_{tone}"
```

### 2.3. Transcript Slicing and Tone Injection (`ai_summarizer.py`)

#### A. Transcript Slicing

A new function is required to slice the full transcript.

```python
# In ai_summarizer.py (New function)
def _slice_transcript(self, full_transcript: str, start_time: str, end_time: str) -> str:
    """Slices the full transcript based on MM:SS timestamps."""
    # 1. Convert MM:SS strings to total seconds.
    # 2. Find the closest text segment start/end times in the transcript data.
    # 3. Return the text content between those points.
    # 4. Handle edge cases (start > end, out of bounds).
    pass # Implementation details to be handled by the coding assistant
```

#### B. Tone Injection

The `generate_summary` function must pass the `tone` and the sliced transcript.

```python
# In ai_summarizer.py (Conceptual change)
def generate_summary(self, video_id, mode, start_time, end_time, tone):
    # 1. Get full transcript (from DB or yt-dlp)
    # 2. Sliced_transcript = self._slice_transcript(full_transcript, start_time, end_time)
    # 3. Inject tone into the prompt template:
    #    final_prompt = config["prompt"].format(..., tone=tone)
    # 4. Call the AI with the sliced_transcript and final_prompt
    pass
```

## 3. Phase 2: Frontend Integration (Unified Control Panel)

### 3.1. Component Structure

A new component, `PersonalizationControlPanel.jsx`, will replace the existing Mode Selector.

```
PersonalizationControlPanel.jsx
├── ModeSelector (Quick vs In-Depth)
├── VideoSegmentSelector (Start/End Time Inputs)
└── ToneSelector (Dropdown/Radio for Tone)
```

### 3.2. UX Flow

1.  The user enters the URL.
2.  The `PersonalizationControlPanel` is visible below the URL input.
3.  The user selects Mode, enters Timestamps (optional), and selects Tone (optional).
4.  The "Generate Summary" button collects all these parameters and sends them in the API call.

## 4. Guardrails and Safety Measures

| Guardrail | Implementation | Rationale |
| :--- | :--- | :--- |
| **Timestamp Validation** | Backend validation in `_slice_transcript` to ensure `start_time` < `end_time` and times are valid MM:SS format. | Prevents API errors and ensures graceful handling. |
| **Tone Default** | Backend defaults `tone` to "Objective" if not provided. | Ensures the prompt always has a valid tone instruction. |
| **Caching Integrity** | All 5 parameters (`video_id`, `mode`, `start`, `end`, `tone`) are included in the cache key. | Guarantees a unique summary for every unique request. |
| **Backward Compatibility** | Frontend defaults `start_time` to "00:00" and `end_time` to "end" if the user does not interact with the new controls. | Ensures the system still works as before for simple URL inputs. |

## 5. Final Coding Prompt

I will now create the final prompt that ties this guide and all previous context together.
