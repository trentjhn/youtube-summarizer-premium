# Phase 4 Testing Guide

## Quick Start

The application is currently running:
- **Frontend:** http://localhost:5175/
- **Backend:** http://localhost:5001/

---

## Test Scenarios

### 1. Basic Functionality Test (Backward Compatibility)

**Objective:** Verify Phase 4 doesn't break existing functionality

**Steps:**
1. Open http://localhost:5175/
2. Paste a YouTube URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
3. Keep default settings (Quick mode, full video, Objective tone)
4. Click "Generate Summary"
5. Verify summary generates successfully

**Expected Result:** ✅ Summary generated with no errors

---

### 2. Timestamp Slicing Test

**Objective:** Test segment-based summarization

**Test Case A: Valid Segment (60+ seconds)**
1. Paste a YouTube URL
2. Click "Advanced Options" to expand
3. Uncheck "Summarize entire video"
4. Enter start time: `00:00`
5. Enter end time: `01:30` (90 seconds)
6. Click "Generate Summary"

**Expected Result:** ✅ Summary generated for first 90 seconds only

**Test Case B: Invalid Segment (< 60 seconds)**
1. Uncheck "Summarize entire video"
2. Enter start time: `00:00`
3. Enter end time: `00:30` (30 seconds)
4. Click "Generate Summary"

**Expected Result:** ❌ Error message: "Segment duration (30 seconds) is too short. Minimum is 60 seconds."

**Test Case C: Invalid Time Range (Start > End)**
1. Enter start time: `01:00`
2. Enter end time: `00:30`
3. Click "Generate Summary"

**Expected Result:** ❌ Error message: "Start time must be before end time"

---

### 3. Tone Preference Test

**Objective:** Test all 5 tone options

**Test Each Tone:**
1. Paste a YouTube URL
2. Click "Advanced Options"
3. Select a tone:
   - 🎯 Objective (Default)
   - 🎓 Academic
   - 💬 Casual
   - 🤔 Skeptical
   - ⚡ Provocative
4. Generate summary
5. Review output style

**Expected Results:**
- ✅ **Objective:** Neutral, balanced tone
- ✅ **Academic:** Formal language, precise terminology
- ✅ **Casual:** Conversational, easy-to-read
- ✅ **Skeptical:** Critical evaluation, questioning tone
- ✅ **Provocative:** Strong language, debate-stimulating

---

### 4. Combined Features Test

**Objective:** Test timestamp + tone together

**Steps:**
1. Paste a YouTube URL
2. Select "In-Depth" mode
3. Click "Advanced Options"
4. Uncheck "Summarize entire video"
5. Enter start time: `01:00`
6. Enter end time: `03:00` (2 minutes)
7. Select "Academic" tone
8. Generate summary

**Expected Result:** ✅ In-depth summary of 2-minute segment in academic tone

---

### 5. UI/UX Test

**Objective:** Verify user interface works correctly

**Checklist:**
- [ ] Mode selector cards are clickable
- [ ] Selected mode is highlighted
- [ ] "Advanced Options" button expands/collapses smoothly
- [ ] Timestamp inputs validate format in real-time
- [ ] Error messages display clearly
- [ ] All controls disabled during processing
- [ ] Loading spinner shows during processing
- [ ] Summary displays correctly after processing

---

### 6. Responsive Design Test

**Objective:** Verify mobile compatibility

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test at different screen sizes:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)

**Expected Results:**
- ✅ Layout adapts to screen size
- ✅ All controls remain accessible
- ✅ Text remains readable
- ✅ No horizontal scrolling

---

### 7. Caching Test

**Objective:** Verify cache works with new parameters

**Test Case A: Same Video, Different Segments**
1. Process video with segment 00:00 to 01:00
2. Process same video with segment 01:00 to 02:00
3. Process same video with segment 00:00 to 01:00 again

**Expected Result:** ✅ Third request returns cached result instantly

**Test Case B: Same Video, Different Tones**
1. Process video with Objective tone
2. Process same video with Academic tone
3. Process same video with Objective tone again

**Expected Result:** ✅ Third request returns cached result instantly

---

### 8. Error Handling Test

**Objective:** Verify graceful error handling

**Test Cases:**
- [ ] Invalid YouTube URL
- [ ] Video with no transcript
- [ ] Invalid timestamp format (e.g., "abc")
- [ ] Start time beyond video length
- [ ] Network error during processing

**Expected Results:** All errors display user-friendly messages

---

### 9. Feature Flag Test

**Objective:** Verify instant rollback capability

**Steps:**
1. Open `youtube-summarizer/src/routes/video.py`
2. Set `USE_PERSONALIZATION_SUITE = False`
3. Restart backend
4. Open `youtube-summarizer-frontend/src/App.jsx`
5. Set `USE_PERSONALIZATION_SUITE = false`
6. Restart frontend
7. Test application

**Expected Result:** ✅ Advanced options hidden, system works with basic features only

---

## Backend Unit Tests

**Run automated tests:**
```bash
cd youtube-summarizer
python test_phase4_backend.py
```

**Expected Output:**
```
=== Testing _parse_timestamp() ===
✅ All 5 tests passing

=== Testing _slice_transcript() ===
✅ All 7 tests passing

=== Testing Tone Parameter ===
✅ All 7 tests passing

TESTING COMPLETE
```

---

## Performance Benchmarks

**Metrics to Monitor:**
- [ ] API response time (should be < 30 seconds for quick mode)
- [ ] Cache hit rate (should be > 80% for repeated requests)
- [ ] Memory usage (should remain stable)
- [ ] No memory leaks during extended use

---

## Known Limitations

1. **yt-dlp Timestamp Extraction:** Currently returns empty `raw_segments`. Timestamp slicing only works with YouTube API extraction method.
2. **Minimum Segment Length:** 60 seconds enforced to ensure meaningful summaries.
3. **Tone Consistency:** AI may not always perfectly match requested tone (depends on model behavior).

---

## Troubleshooting

### Issue: "Timestamp slicing requested but raw_segments not available"

**Cause:** Video transcript extracted via yt-dlp (fallback method)  
**Solution:** This is expected. System will use full transcript and log a warning.

### Issue: Advanced options not showing

**Cause:** Feature flag disabled  
**Solution:** Check `USE_PERSONALIZATION_SUITE` in both backend and frontend

### Issue: Tone doesn't seem to change output

**Cause:** AI model may not always follow tone instructions perfectly  
**Solution:** This is a known limitation. Try with different videos or more distinct tones.

---

## Success Criteria

Phase 4 is considered successful if:
- ✅ All backend unit tests pass
- ✅ All manual test scenarios pass
- ✅ No regressions in existing functionality
- ✅ Feature flags work correctly
- ✅ UI is responsive and accessible
- ✅ Error handling is graceful
- ✅ Performance is acceptable

---

**Happy Testing!** 🧪

