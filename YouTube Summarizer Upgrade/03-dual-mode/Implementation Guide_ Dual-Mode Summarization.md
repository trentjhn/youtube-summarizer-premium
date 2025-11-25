# Implementation Guide: Dual-Mode Summarization

## 1. Overview

This guide provides step-by-step instructions for implementing the dual-mode summarization feature (Quick vs. In-Depth) into your YouTube Summarizer application.

**Complexity:** Medium
**Estimated Time:** 15 hours

---

## 2. Backend Implementation

### 2.1. Update `ai_summarizer.py`

**File:** `youtube-summarizer/src/services/ai_summarizer.py`

#### Step 1: Add New Prompts

Add two new prompt constants at the top of the file. `QUICK_SUMMARY_PROMPT_V3` will be a slightly more concise version of your current v3.0 prompt. `INDEPTH_SUMMARY_PROMPT_V3` will be an enhanced version with instructions for the new JSON fields.

```python
# Add this at the top of the file

QUICK_SUMMARY_PROMPT_V3 = """
# ROLE & GOAL
You are a world-class summarization engine. Your goal is to create a concise, accurate, and insightful summary. Adhere to these principles:

# CORE PRINCIPLES
1.  **BE DIRECT & CONCISE:** No filler words. Get straight to the point.
2.  **PRESERVE CONTEXT & ATTRIBUTION:** Clearly attribute quotes and references.
3.  **FAITHFUL REPRESENTATION:** Do not soften or sanitize the content.
4.  **TONE MATCHING:** Match the speaker's tone.

# JSON OUTPUT STRUCTURE (5 Components)
Return a valid JSON object with these fields: `quick_takeaway`, `key_points`, `topics`, `timestamps`, `full_summary`.

# INSTRUCTIONS
- `quick_takeaway`: Max 150 characters.
- `key_points`: 5-7 concise points.
- `full_summary`: 5-8 well-developed paragraphs.

# TRANSCRIPT
---
{transcript}
---

Video Title: {title}
"""

INDEPTH_SUMMARY_PROMPT_V3 = """
# ROLE & GOAL
You are a world-class summarization engine. Your goal is to create a comprehensive, in-depth analysis. Adhere to these principles with absolute precision:

# CORE PRINCIPLES (NON-NEGOTIABLE)
(Same as your current v3.0 prompt with detailed instructions)

# JSON OUTPUT STRUCTURE (8 Components)
Return a valid JSON object with these fields: `quick_takeaway`, `key_points`, `topics`, `timestamps`, `full_summary`, `detailed_analysis`, `key_quotes`, `arguments`.

# INSTRUCTIONS
- `quick_takeaway`: Max 150 characters.
- `key_points`: 10-15 detailed points.
- `full_summary`: 8-12 comprehensive paragraphs.
- `detailed_analysis`: A deeper dive into each topic.
- `key_quotes`: 3-5 important verbatim quotes.
- `arguments`: Main arguments and counterpoints.

# TRANSCRIPT
---
{transcript}
---

Video Title: {title}
"""
```

#### Step 2: Update `PROMPT_VERSION`

Change the global prompt version to reflect the new modes.

```python
PROMPT_VERSION = "v3.0" # Keep this as the base version for both modes
```

#### Step 3: Update `AISummarizer` Class

Modify the `__init__` method to include the mode configurations.

```python
class AISummarizer:
    def __init__(self):
        self.client = OpenAI()
        self.mode_configs = {
            "quick": {
                "prompt": QUICK_SUMMARY_PROMPT_V3,
                "chunking_threshold": 60,
                "chunk_size": 3000,
                "max_tokens": 2500
            },
            "indepth": {
                "prompt": INDEPTH_SUMMARY_PROMPT_V3,
                "chunking_threshold": 30,
                "chunk_size": 1500,
                "max_tokens": 8000
            }
        }
```

#### Step 4: Update `generate_summary` Method

Replace the existing `generate_summary` method with the new mode-aware version.

```python
def generate_summary(self, transcript: str, title: str, mode: str = "quick") -> dict:
    config = self.mode_configs.get(mode, self.mode_configs["quick"])
    
    estimated_duration = self._estimate_duration_minutes(transcript)
    
    if estimated_duration > config["chunking_threshold"]:
        logger.info(f"Video duration estimated at {estimated_duration:.1f} minutes. Using adaptive chunking for {mode} mode.")
        return self._summarize_in_chunks(transcript, title, mode, config)
    else:
        logger.info(f"Video duration estimated at {estimated_duration:.1f} minutes. Using single-pass summarization for {mode} mode.")
        return self._summarize_single_pass(transcript, title, mode, config)
```

#### Step 5: Update `_summarize_single_pass` and `_summarize_in_chunks`

Modify these methods to accept and use the `mode` and `config` parameters.

```python
def _summarize_single_pass(self, transcript: str, title: str, mode: str, config: dict) -> dict:
    prompt = config["prompt"].format(transcript=transcript, title=title)
    # ... rest of the logic using config["max_tokens"] ...

def _summarize_in_chunks(self, transcript: str, title: str, mode: str, config: dict) -> dict:
    chunks = self._split_transcript(transcript, chunk_size=config["chunk_size"])
    # ... rest of the logic ...
    final_summary = self._summarize_single_pass(meta_transcript, title, mode, config)
    return final_summary
```

### 2.2. Update `main.py`

**File:** `youtube-summarizer/src/main.py`

#### Step 1: Update `/api/process-video` Endpoint

Modify the endpoint to accept and validate the `mode` parameter.

```python
@app.route("/api/process-video", methods=["POST"])
def process_video():
    url = request.json.get("url")
    mode = request.json.get("mode", "quick")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if mode not in ["quick", "indepth"]:
        return jsonify({"error": "Invalid mode specified"}), 400

    # ... existing logic ...

    # Update cache key generation
    cache_key = f"{video_id}_{mode}_{PROMPT_VERSION}"
    cached_summary = cache.get(cache_key)

    if cached_summary:
        # ... return cached summary ...

    # ... transcript extraction ...

    # Pass mode to the summarizer
    summary_json = ai_summarizer.generate_summary(transcript, title, mode)

    # ... cache and store summary ...
    cache.set(cache_key, summary_json)
    # ...
```

---

## 3. Frontend Implementation

### 3.1. Add Mode Selector UI

**File:** `youtube-summarizer-frontend/src/components/VideoInputForm.jsx` (or similar)

#### Step 1: Add State for Mode

```jsx
import { useState } from "react";

const VideoInputForm = ({ onSubmit }) => {
    const [url, setUrl] = useState("");
    const [mode, setMode] = useState("quick"); // Default mode

    const handleSubmit = () => {
        onSubmit(url, mode);
    };

    // ...
};
```

#### Step 2: Add Mode Selector Component

Create a new component for the mode selector.

```jsx
// ModeSelector.jsx
const ModeSelector = ({ selectedMode, onSelectMode }) => (
    <div>
        <h3>Summarization Mode</h3>
        <div style={{ display: "flex", gap: "1rem" }}>
            <div 
                className={`mode-card ${selectedMode === "quick" ? "selected" : ""}`}
                onClick={() => onSelectMode("quick")}
            >
                <h4>🚀 Quick Summary</h4>
                <p>Get the essential insights in minimal time.</p>
                <p>⏱️ ~30 seconds</p>
            </div>
            <div 
                className={`mode-card ${selectedMode === "indepth" ? "selected" : ""}`}
                onClick={() => onSelectMode("indepth")}
            >
                <h4>🔍 In-Depth Analysis</h4>
                <p>A comprehensive breakdown of the entire video.</p>
                <p>⏱️ ~60-90 seconds</p>
            </div>
        </div>
    </div>
);
```

Add corresponding CSS for `.mode-card` and `.selected`.

#### Step 3: Integrate into Form

```jsx
// VideoInputForm.jsx
return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        {/* URL Input */}
        <ModeSelector selectedMode={mode} onSelectMode={setMode} />
        <button type="submit">Generate Summary</button>
    </form>
);
```

### 3.2. Update API Call

**File:** `youtube-summarizer-frontend/src/services/api.js` (or similar)

Modify the function that calls the backend to include the `mode`.

```javascript
export const processVideo = async (url, mode) => {
    const response = await fetch("/api/process-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, mode })
    });
    // ...
};
```

### 3.3. Add Conditional Rendering for In-Depth Summary

**File:** `youtube-summarizer-frontend/src/components/SummaryView/RightSidebar.jsx` (or similar)

Modify the component to render the additional sections if they exist in the summary data.

```jsx
const RightSidebar = ({ summary }) => {
    const isIndepth = summary.hasOwnProperty("detailed_analysis");

    return (
        <div className="right-sidebar">
            {/* Existing tabs: AI Chat, Notes */}

            {isIndepth && (
                <div className="indepth-sections">
                    <h3>In-Depth Content</h3>
                    <CollapsibleSection title="Detailed Analysis">
                        {summary.detailed_analysis.map((item, index) => (
                            <div key={index}>{/* Render analysis item */}</div>
                        ))}
                    </CollapsibleSection>
                    <CollapsibleSection title="Key Quotes">
                        {summary.key_quotes.map((quote, index) => (
                            <blockquote key={index}>{quote}</blockquote>
                        ))}
                    </CollapsibleSection>
                    <CollapsibleSection title="Arguments">
                        {summary.arguments.map((arg, index) => (
                            <div key={index}>{/* Render argument item */}</div>
                        ))}
                    </CollapsibleSection>
                </div>
            )}
        </div>
    );
};
```

---

## 4. Testing and Validation

### 4.1. Test Plan

1.  **Quick Mode - Short Video (<30 min):**
    -   Verify single-pass summarization is used.
    -   Verify summary is concise (5-7 key points).
    -   Verify processing time is fast (~30s).

2.  **Quick Mode - Long Video (>60 min):**
    -   Verify adaptive chunking is triggered (with 60 min threshold).
    -   Verify summary is still concise.

3.  **In-Depth Mode - Short Video (<30 min):**
    -   Verify single-pass summarization is used.
    -   Verify summary is comprehensive (10-15 key points, 8 components in JSON).

4.  **In-Depth Mode - Long Video (>30 min):**
    -   Verify adaptive chunking is triggered (with 30 min threshold).
    -   Verify summary is highly detailed and granular.

5.  **Caching:**
    -   Process a video in Quick mode.
    -   Process the same video again in Quick mode (should be instant from cache).
    -   Process the same video in In-Depth mode (should generate a new summary).
    -   Process the same video again in In-Depth mode (should be instant from cache).

6.  **UI/UX:**
    -   Verify mode selector works correctly.
    -   Verify default mode is "Quick".
    -   Verify conditional rendering of in-depth sections works.

### 4.2. Quality Assurance

-   Compare the output of both modes for the same video.
-   Ensure Quick mode provides a good high-level overview.
-   Ensure In-Depth mode provides significant additional value.

---

## 5. Rollout

1.  Deploy backend changes.
2.  Deploy frontend changes.
3.  The new feature will be live. No database migration is needed.

---

## 6. Future Considerations

-   **"Regenerate in In-Depth Mode":** Add a button to the Quick summary view to re-process the video in In-Depth mode.
-   **Usage Analytics:** Track which mode is used more often to inform future development.
-   **Cost Control:** Implement a daily or monthly budget limit for API calls, especially for In-Depth mode.
