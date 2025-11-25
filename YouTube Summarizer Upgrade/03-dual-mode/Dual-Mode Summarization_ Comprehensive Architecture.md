# Dual-Mode Summarization: Comprehensive Architecture

## 1. Guiding Principles

- **Modularity:** Each mode (Quick, In-Depth) should be a self-contained unit of logic.
- **Clarity:** The value proposition for each mode must be clear to the user.
- **Maintainability:** Code should be easy to debug, update, and extend.
- **Performance:** Quick mode must be fast; In-depth mode must be thorough.
- **Backward Compatibility:** The system should not break if the mode is not specified.

---

## 2. Overall System Flow

1.  **User Enters URL:** User pastes a YouTube URL into the frontend.
2.  **User Selects Mode:** User chooses between "Quick Summary" (default) and "In-Depth Analysis".
3.  **Frontend Sends Request:** Frontend sends a `POST` request to `/api/process-video` with the `url` and selected `mode`.
4.  **Backend Receives Request:** Flask app validates the `url` and `mode`.
5.  **Cache Check:** The system constructs a mode-aware cache key (e.g., `video_id_quick_v3.0`) and checks if a valid summary exists.
    -   **Cache Hit:** If found, the cached JSON summary is returned immediately.
    -   **Cache Miss:** If not found, proceed to processing.
6.  **Transcript Extraction:** `yt-dlp` extracts the video transcript (no changes to this system).
7.  **Adaptive Summarization:** The `AISummarizer` service is called with the `transcript`, `title`, and `mode`.
    -   It estimates the video duration.
    -   Based on the `mode`, it selects the appropriate prompt, chunking threshold, and token limits.
    -   It generates the summary (either single-pass or chunked).
8.  **JSON Generation:** The AI returns a structured JSON object (5 components for Quick, 8 for In-Depth).
9.  **Cache & Store:** The backend caches the new summary with the mode-aware key and stores it in the database.
10. **Backend Sends Response:** The backend sends the JSON summary to the frontend.
11. **Frontend Renders UI:** The React frontend receives the JSON and conditionally renders the UI.
    -   If the JSON has 8 components, it displays the enhanced layout with extra sections.
    -   If it has 5 components, it displays the standard layout.

---

## 3. Prompt Engineering Strategy

Two separate, highly-engineered prompts will be used.

### 3.1. `QUICK_SUMMARY_PROMPT_V3`

**Goal:** Speed and conciseness.

**Key Instructions:**
-   "Be extremely concise. Focus only on the most essential insights."
-   "Aim for clarity and speed. Do not include unnecessary details."
-   "Return a maximum of 5 key points and 5 paragraphs in the full summary."

**Parameters:**
-   `max_tokens`: 2500
-   `temperature`: 0.3 (more factual, less creative)

### 3.2. `INDEPTH_SUMMARY_PROMPT_V3`

**Goal:** Comprehensiveness and detail.

**Key Instructions:**
-   "Provide a comprehensive, in-depth analysis. Include all important details, nuances, and context."
-   "Extract key quotes verbatim. Analyze main arguments and counterpoints."
-   "Return 10-15 key points and 8-12 paragraphs in the full summary."
-   "Populate the additional JSON fields: `detailed_analysis`, `key_quotes`, and `arguments`."

**Parameters:**
-   `max_tokens`: 8000 (allows for much longer output)
-   `temperature`: 0.5 (slightly more creative for analysis)

---

## 4. Backend Architecture (`ai_summarizer.py`)

### 4.1. Class Structure

The `AISummarizer` class will be updated to manage mode-specific configurations.

```python
class AISummarizer:
    def __init__(self):
        self.client = OpenAI()
        self.mode_configs = {
            "quick": {
                "prompt": QUICK_SUMMARY_PROMPT_V3,
                "chunking_threshold": 60,  # minutes
                "chunk_size": 3000,        # words
                "max_tokens": 2500
            },
            "indepth": {
                "prompt": INDEPTH_SUMMARY_PROMPT_V3,
                "chunking_threshold": 30,  # minutes
                "chunk_size": 1500,        # words
                "max_tokens": 8000
            }
        }

    def generate_summary(self, transcript: str, title: str, mode: str = "quick") -> dict:
        # ...
```

### 4.2. `generate_summary` Method

This method will be the main entry point and will orchestrate the process based on the selected mode.

```python
def generate_summary(self, transcript: str, title: str, mode: str = "quick") -> dict:
    config = self.mode_configs.get(mode, self.mode_configs["quick"])
    
    estimated_duration = self._estimate_duration_minutes(transcript)
    
    if estimated_duration > config["chunking_threshold"]:
        return self._summarize_in_chunks(transcript, title, mode, config)
    else:
        return self._summarize_single_pass(transcript, title, mode, config)
```

### 4.3. `_summarize_single_pass` Method

This method will now use the mode-specific configuration.

```python
def _summarize_single_pass(self, transcript: str, title: str, mode: str, config: dict) -> dict:
    prompt = config["prompt"].format(transcript=transcript, title=title)
    
    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[...],
        max_tokens=config["max_tokens"],
        temperature=0.4  # Can also be part of config
    )
    
    # ... JSON parsing and validation ...
```

### 4.4. `_summarize_in_chunks` Method

This method will also use the mode-specific configuration for chunking.

```python
def _summarize_in_chunks(self, transcript: str, title: str, mode: str, config: dict) -> dict:
    chunks = self._split_transcript(transcript, chunk_size=config["chunk_size"])
    
    # ... summarize each chunk ...
    
    # Final summarization of meta-transcript
    final_summary = self._summarize_single_pass(meta_transcript, title, mode, config)
    return final_summary
```

---

## 5. API Architecture (`main.py`)

### 5.1. `/api/process-video` Endpoint

The endpoint will be updated to accept and validate the `mode` parameter.

```python
@app.route("/api/process-video", methods=["POST"])
def process_video():
    url = request.json.get("url")
    mode = request.json.get("mode", "quick")  # Default to "quick"

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if mode not in ["quick", "indepth"]:
        return jsonify({"error": "Invalid mode specified"}), 400

    # ... existing logic ...

    # Pass mode to the summarizer
    summary_json = ai_summarizer.generate_summary(transcript, title, mode)

    # ... existing logic ...
```

---

## 6. Caching Architecture

### 6.1. Mode-Aware Cache Key

The `CacheManager` (or equivalent) will be updated to include the `mode` in the cache key.

```python
# In your caching utility
PROMPT_VERSION = "v3.0" # This can be a global constant

def get_cache_key(video_id: str, mode: str) -> str:
    # Use a hash to keep the key length consistent
    key_string = f"{video_id}_{mode}_{PROMPT_VERSION}"
    return hashlib.sha256(key_string.encode()).hexdigest()

# When checking cache:
cache_key = get_cache_key(video_id, mode)
cached_summary = cache.get(cache_key)

# When setting cache:
cache.set(cache_key, summary_json)
```

---

## 7. Frontend Architecture

### 7.1. State Management (React)

The component responsible for the video input will manage the selected mode.

```jsx
// In VideoInputForm.jsx
import { useState } from "react";

const VideoInputForm = () => {
    const [url, setUrl] = useState("");
    const [mode, setMode] = useState("quick"); // Default mode

    const handleSubmit = async () => {
        // ... API call ...
        await api.processVideo(url, mode);
    };

    return (
        <div>
            {/* URL Input */}
            <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} />

            {/* Mode Selector */}
            <div>
                <button 
                    className={mode === "quick" ? "selected" : ""}
                    onClick={() => setMode("quick")}
                >
                    🚀 Quick Summary
                </button>
                <button 
                    className={mode === "indepth" ? "selected" : ""}
                    onClick={() => setMode("indepth")}
                >
                    🔍 In-Depth Analysis
                </button>
            </div>

            <button onClick={handleSubmit}>Generate Summary</button>
        </div>
    );
};
```

### 7.2. Conditional Rendering

The component that displays the summary will check for the presence of the enhanced fields.

```jsx
// In SummaryView.jsx

const SummaryView = ({ summary }) => {
    const isIndepth = summary.hasOwnProperty("detailed_analysis");

    return (
        <div className="three-pane-layout">
            {/* Left Sidebar (Quick Takeaway, Key Points, Topics) */}
            <LeftSidebar summary={summary} />

            {/* Main Content (Full Summary) */}
            <MainContent summary={summary} />

            {/* Right Sidebar (AI Chat, Notes, and new sections) */}
            <RightSidebar summary={summary} isIndepth={isIndepth} />
        </div>
    );
};

// In RightSidebar.jsx
const RightSidebar = ({ summary, isIndepth }) => {
    return (
        <div>
            {/* AI Chat and Notes tabs */}

            {isIndepth && (
                <>
                    <DetailedAnalysisSection analysis={summary.detailed_analysis} />
                    <KeyQuotesSection quotes={summary.key_quotes} />
                    <ArgumentsSection arguments={summary.arguments} />
                </>
            )}
        </div>
    );
};
```

---

## 8. Database

**No changes are required.** The existing `summary` column of type `JSON` can store both the 5-component and 8-component structures without any modification. This is a major advantage of using a flexible data type like JSON.

---

## 9. UX/UI Flow

### 9.1. Mode Selection

A clear, visually distinct component will be added below the URL input field. It will consist of two large, clickable cards.

**Visual Mockup:**

```
  Summarization Mode
  ┌──────────────────────────┐  ┌──────────────────────────┐
  │ 🚀 Quick Summary         │  │ 🔍 In-Depth Analysis     │
  │ Get the essential insights │  │ A comprehensive breakdown  │
  │ in minimal time.         │  │ of the entire video.     │
  │                          │  │                          │
  │ ⏱️ ~30 seconds           │  │ ⏱️ ~60-90 seconds        │
  └──────────────────────────┘  └──────────────────────────┘
  (Default selected with a blue border)
```

### 9.2. In-Depth Summary Display

The right sidebar ("The Toolkit") will be enhanced to include the new sections, likely as additional tabs or collapsible accordions.

**Right Sidebar Tabs:**

`[ AI Chat ] [ Notes ] [ Analysis ] [ Quotes ] [ Arguments ]`

This keeps the interface clean while providing access to the rich, in-depth content.

---

## 10. Conclusion

This architecture provides a robust, maintainable, and user-friendly solution for implementing the dual-mode summarization feature. It cleanly separates the logic for each mode, provides a clear UX, and leverages the existing system architecture effectively. The implementation is of medium complexity but offers a significant enhancement to the product.
