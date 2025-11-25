# Implementation Prompt for AI Coding Assistant

## Your Mission

You are tasked with upgrading a working YouTube Video Summarizer application to a premium, three-pane interactive digest interface. This is an **incremental upgrade**, not a complete rewrite. You must implement all changes with strict adherence to safety guardrails, backward compatibility, and professional software engineering practices.

---

## What You're Receiving

I'm providing you with **5 comprehensive documents** that contain everything you need:

1. **`master_implementation_guide_with_guardrails.md`** - The core implementation plan with all safety measures
2. **`premium_ui_ux_design.md`** - The complete design vision and philosophy
3. **`premium_ui_implementation_guide.md`** - Detailed code examples for all components
4. **`integration_assessment.md`** - Analysis of what changes and what stays the same
5. **`cache_versioning_guide.md`** - The caching strategy (already implemented, for context)

---

## Critical Requirements

### 1. **Safety First**

You MUST implement these guardrails:

-   **Graceful Degradation:** If AI returns invalid JSON, the system must fall back to a simple, valid format and log the error.
-   **Backward Compatibility:** The system must handle both old (text) and new (JSON) summary formats.
-   **Input Validation:** All API endpoints must validate and sanitize user input.
-   **Idempotent Scripts:** Database migration scripts must be safe to run multiple times.
-   **Feature Flags:** Implement toggles to switch between old and new UI for safe testing.
-   **Error Handling:** Every external call (OpenAI API, database queries) must have proper `try...except` blocks.

### 2. **Preserve Core Functionality**

**DO NOT MODIFY:**
-   Transcript extraction system (yt-dlp)
-   Video processing pipeline
-   Caching logic
-   Database schema (except the `summary` column type)
-   Flask routing structure
-   Video input form

**ONLY MODIFY:**
-   `ai_summarizer.py` (to return JSON)
-   `models.py` (one column type change)
-   Frontend UI components (new components, old ones can coexist)

### 3. **Testing is Mandatory**

After each phase, you MUST:
-   Test that the change works as expected
-   Test that existing functionality still works
-   Test error cases (what if AI returns invalid JSON? What if data is missing?)
-   Verify the rollback plan works

---

## Implementation Phases (Execute in Order)

### Phase 1: Backend JSON Implementation

**Files to Modify:**
1. `youtube-summarizer/src/services/ai_summarizer.py`
2. `youtube-summarizer/src/database/models.py`

**What to Do:**
1. Update the `COMPREHENSIVE_SUMMARY_PROMPT` to request structured JSON (full prompt provided in the implementation guide)
2. Modify `generate_summary()` to:
   - Return `dict` instead of `str`
   - Parse the AI's JSON response
   - Implement a `_get_fallback_summary()` method for when JSON parsing fails
   - Add comprehensive error logging
3. Change the `summary` column in `models.py` from `db.Text` to `db.JSON`
4. Create an idempotent migration script `migrate_db.py` to convert existing text summaries to JSON format

**Testing:**
-   Process a new video and verify the database stores a JSON object
-   Manually test the fallback by simulating a JSON parse error
-   Run the migration script twice to confirm it's idempotent

### Phase 2: Frontend Component Structure

**Files to Create:**
-   `src/components/SummaryView/SummaryView.jsx` (main container)
-   `src/components/SummaryView/Header.jsx`
-   `src/components/SummaryView/LeftSidebar.jsx`
-   `src/components/SummaryView/MainContent.jsx`
-   `src/components/SummaryView/RightSidebar.jsx`
-   `src/components/SummaryView/[all other subcomponents]`
-   `src/components/SummaryView/styles.css`

**What to Do:**
1. Create the three-pane layout as specified in the implementation guide
2. Implement data validation in `SummaryView.jsx` to ensure the summary is in the expected format
3. Add a feature flag in `App.jsx` to toggle between old and new UI:
   ```jsx
   const USE_PREMIUM_UI = true; // Set to false to revert
   ```
4. Ensure all interactive features work: topic scrolling, timestamp links, sidebar toggles

**Testing:**
-   Toggle the feature flag to `false` and confirm the old UI still works
-   Toggle to `true` and verify the new UI renders correctly
-   Test with a fallback summary to ensure graceful error handling

### Phase 3: AI Chat Functionality

**Files to Modify:**
-   `youtube-summarizer/src/main.py` (add new endpoint)

**What to Do:**
1. Create a new `/api/chat` endpoint with:
   - Input validation (check for `video_id` and `message`)
   - Context limiting (max 12,000 characters of transcript)
   - Proper error responses (400 for bad input, 404 for missing video)
2. Implement the `AIChatPanel.jsx` component to call this endpoint

**Testing:**
-   Send a request with missing `video_id` to confirm 400 error
-   Test chat with a valid request
-   Verify the chat history persists during the session

### Phase 4: Final Polish & Deployment Prep

**What to Do:**
1. Review all code for consistency and best practices
2. Add comments to complex logic
3. Ensure all console.log statements are removed or converted to proper logging
4. Run the full testing checklist (provided in the master guide)
5. Document any deviations from the plan

---

## Expected Deliverables

Please provide:

1. **All modified files** with complete, production-ready code
2. **The migration script** (`migrate_db.py`)
3. **A summary of changes** made to each file
4. **Any deviations** from the implementation guide and the reasons why
5. **Confirmation** that all tests in the checklist have passed

---

## Rollback Plan (For Reference)

If a critical issue arises:
1. Set `USE_PREMIUM_UI = false` in the frontend
2. Revert `ai_summarizer.py` to the old version
3. The database can remain as-is (JSON column is compatible)

---

## Important Notes

-   **Don't rush.** Implement each phase completely before moving to the next.
-   **Test thoroughly.** Each phase has specific test cases.
-   **Ask questions.** If anything is unclear, flag it before proceeding.
-   **Think about edge cases.** What if the transcript is empty? What if the AI times out?
-   **Use modern React patterns.** Hooks, functional components, proper state management.
-   **Make it production-ready.** This isn't a prototype; it's a real upgrade.

---

## Success Criteria

The implementation is successful when:

1. New videos generate structured JSON summaries
2. Old summaries are migrated and display correctly
3. The three-pane UI renders and all interactions work
4. AI chat functionality is operational
5. The feature flag allows instant rollback to the old UI
6. All error cases are handled gracefully
7. The system feels polished, professional, and premium

---

## Final Checklist Before Submission

-   [ ] All code is complete and tested
-   [ ] Migration script is idempotent
-   [ ] Feature flag is implemented
-   [ ] Error handling is comprehensive
-   [ ] Rollback plan is verified
-   [ ] All tests pass
-   [ ] Code is clean and commented

You have everything you need. Proceed with confidence, and build something exceptional.
