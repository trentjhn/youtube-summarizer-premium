# Feature 4: Tone and Style Preference Analysis

## 1. Feature Concept

**Concept:** Allow users to select a specific tone or style for the final summary output (e.g., "Academic," "Casual," "Provocative," "Skeptical").

**Use Case:** A user wants a summary of a technical video presented in a "Casual" tone for easy reading, or a summary of a political video presented in a "Skeptical" tone for critical analysis.

## 2. Technical Feasibility

**Verdict: Highly Feasible.** This is a pure prompt engineering change that leverages the existing architecture.

### 2.1. Backend Considerations

| Component | Impact | Implementation Approach |
| :--- | :--- | :--- |
| **API Design** | **Low.** The `/api/process-video` endpoint needs one optional parameter: `tone`. | Add `tone` (e.g., a string like "Academic" or "Casual") to the request body. |
| **Prompt Logic** | **High.** The selected tone must be injected into the prompt template. | The prompt template will include a placeholder: `TONE: {tone}`. |
| **Caching** | **High.** The cache key **MUST** be updated to include the selected tone. | New cache key: `video_id_mode_version_start_end_tone`. |
| **Summarization Logic** | **Low.** The core summarization function remains the same, but the output style changes based on the prompt. | The AI model handles the stylistic change based on the injected instruction. |

### 2.2. Prompt Optimization Strategy

The tone preference will be implemented as a **Constraint** within the prompt's instruction set.

**Example Prompt Snippet (for both Quick and In-Depth modes):**

```
# TONE AND STYLE CONSTRAINT
The final summary MUST be written in a {tone} tone. 
- If the tone is 'Academic', use formal language and cite concepts.
- If the tone is 'Casual', use conversational language and contractions.
- If the tone is 'Skeptical', critically evaluate the speaker's claims and highlight assumptions.
```

**Guardrail:** If the user does not select a tone, the system will default to the current **"Faithful Representation"** tone, which is the most objective and true to the source material.

## 3. UX Integration (Unified Control Panel)

The Tone Preference feature is an ideal candidate for the **Unified Personalization Control Panel** (Feature 2).

**Proposed Implementation:**

1.  **Control Panel Section:** Add a new section labeled "Tone and Style" to the Control Panel.
2.  **UI Element:** Use a **Dropdown Menu** or a **Radio Button Group** with 5-7 predefined options (e.g., Academic, Casual, Provocative, Skeptical, Objective).
3.  **Default:** "Objective" (or "Faithful Representation") will be the default selection.

## 4. Updated Implementation Roadmap

This feature is highly complementary to the core functionality and should be implemented alongside the Timestamp feature, as both require similar changes to the API and caching logic.

| Priority | Feature | Implementation Focus | Technical Changes |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Timestamp-Based Summarization** | **Backend Optimization & Latency Reduction** | Update API/Caching to include `start`/`end` time. Implement `_slice_transcript`. |
| **Phase 1.5** | **Tone and Style Preference** | **Personalization & Prompt Optimization** | Update API/Caching to include `tone`. Inject `tone` into both Quick and In-Depth prompts. |
| **Phase 2** | **Unified Control Panel** | **UX Integration & Feature Consolidation** | Create `PersonalizationControlPanel.jsx` to house Mode, Timestamp, and Tone selectors. |
| **Phase 3** | **Credit-Based Pricing** | **Monetization Infrastructure** | Deferred. |

**Conclusion:** The Tone and Style Preference feature is a high-value addition that can be implemented efficiently by bundling it with the Timestamp feature's backend changes. This maintains the focus on core functionality and personalization.
