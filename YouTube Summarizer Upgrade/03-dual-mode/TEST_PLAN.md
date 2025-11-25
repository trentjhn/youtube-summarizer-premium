# Dual-Mode Summarization - Test Plan

**Date:** November 25, 2025  
**Phase:** 3 - Dual-Mode Summarization  
**Status:** Ready for Testing

---

## 🎯 Testing Objectives

1. Verify both modes (Quick and In-Depth) work correctly
2. Ensure mode-specific configurations are applied
3. Validate conditional rendering of in-depth sections
4. Confirm independent caching for each mode
5. Test UI/UX flows and accessibility
6. Verify error handling and edge cases

---

## 🧪 Test Scenarios

### **Test 1: Quick Mode - Short Video (<30 min)**

**Objective:** Verify Quick mode works correctly for short videos

**Test Video:** Any YouTube video under 30 minutes  
**Example:** https://www.youtube.com/watch?v=dQw4w9WgXcQ (3:32)

**Steps:**
1. Open application at http://localhost:5173
2. Enter video URL
3. Select "Quick Summary" mode (should be default)
4. Click "Generate Summary"
5. Wait for processing

**Expected Results:**
- ✅ Processing completes in ~20-40 seconds
- ✅ Summary contains 5 JSON components:
  - `quick_takeaway`
  - `key_points` (5-7 items)
  - `topics`
  - `timestamps`
  - `full_summary` (5-8 paragraphs)
- ✅ No in-depth sections visible (no Detailed Analysis, Key Quotes, or Arguments)
- ✅ Single-pass summarization (check backend logs)

**Backend Verification:**
```bash
# Check logs for:
# - "Mode: quick"
# - "Using single-pass summarization"
# - "Estimated duration: X minutes (below threshold)"
```

---

### **Test 2: In-Depth Mode - Short Video (<30 min)**

**Objective:** Verify In-Depth mode works correctly for short videos

**Test Video:** Same video as Test 1

**Steps:**
1. Open application
2. Enter same video URL
3. Select "In-Depth Analysis" mode
4. Click "Generate Summary"
5. Wait for processing

**Expected Results:**
- ✅ Processing completes in ~40-90 seconds
- ✅ Summary contains 8 JSON components:
  - Standard 5 components (same as Quick mode)
  - `detailed_analysis` (3-5 items)
  - `key_quotes` (3-5 items)
  - `arguments` (3-5 items)
- ✅ In-depth sections visible after full summary:
  - "Detailed Analysis" section with numbered cards
  - "Key Quotes" section with quote-style cards
  - "Arguments & Claims" section with structured cards
- ✅ Visual divider with "In-Depth Analysis" badge
- ✅ Single-pass summarization (check backend logs)

**Backend Verification:**
```bash
# Check logs for:
# - "Mode: indepth"
# - "Using single-pass summarization"
# - "max_tokens: 8000"
```

---

### **Test 3: Quick Mode - Long Video (>60 min)**

**Objective:** Verify Quick mode chunking for long videos

**Test Video:** Any YouTube video over 60 minutes  
**Example:** https://www.youtube.com/watch?v=... (find a 90+ min video)

**Steps:**
1. Open application
2. Enter long video URL
3. Select "Quick Summary" mode
4. Click "Generate Summary"
5. Wait for processing (may take 2-3 minutes)

**Expected Results:**
- ✅ Processing completes in ~2-4 minutes
- ✅ Adaptive chunking triggered (check backend logs)
- ✅ Chunk size: ~3000 words per chunk
- ✅ Summary contains 5 JSON components
- ✅ No in-depth sections visible

**Backend Verification:**
```bash
# Check logs for:
# - "Mode: quick"
# - "Using adaptive chunking"
# - "Estimated duration: X minutes (above 60-minute threshold)"
# - "Splitting into N chunks of ~3000 words"
```

---

### **Test 4: In-Depth Mode - Long Video (>30 min)**

**Objective:** Verify In-Depth mode chunking for long videos

**Test Video:** Any YouTube video over 30 minutes (but under 60 min)  
**Example:** https://www.youtube.com/watch?v=... (find a 45-min video)

**Steps:**
1. Open application
2. Enter video URL
3. Select "In-Depth Analysis" mode
4. Click "Generate Summary"
5. Wait for processing

**Expected Results:**
- ✅ Processing completes in ~3-5 minutes
- ✅ Adaptive chunking triggered (check backend logs)
- ✅ Chunk size: ~1500 words per chunk
- ✅ Summary contains 8 JSON components
- ✅ All in-depth sections visible

**Backend Verification:**
```bash
# Check logs for:
# - "Mode: indepth"
# - "Using adaptive chunking"
# - "Estimated duration: X minutes (above 30-minute threshold)"
# - "Splitting into N chunks of ~1500 words"
```

---

### **Test 5: Independent Caching**

**Objective:** Verify both modes cache independently

**Test Video:** Any short video

**Steps:**
1. Process video in Quick mode (first time)
2. Note processing time (~30 seconds)
3. Process SAME video in Quick mode again
4. Note processing time (should be instant from cache)
5. Process SAME video in In-Depth mode
6. Note processing time (~60 seconds, not cached)
7. Process SAME video in In-Depth mode again
8. Note processing time (should be instant from cache)

**Expected Results:**
- ✅ First Quick mode: ~30 seconds (not cached)
- ✅ Second Quick mode: <1 second (cached)
- ✅ First In-Depth mode: ~60 seconds (not cached, even though Quick was cached)
- ✅ Second In-Depth mode: <1 second (cached)

**Backend Verification:**
```bash
# Check logs for:
# - "Cache miss" for first Quick mode
# - "Cache hit" for second Quick mode
# - "Cache miss" for first In-Depth mode (different cache key)
# - "Cache hit" for second In-Depth mode
```

---

### **Test 6: Mode Selector UI/UX**

**Objective:** Verify mode selector works correctly

**Steps:**
1. Open application
2. Observe mode selector (should default to Quick)
3. Click "In-Depth Analysis" card
4. Observe visual changes
5. Click "Quick Summary" card
6. Observe visual changes
7. Use keyboard (Tab to focus, Enter to select)

**Expected Results:**
- ✅ Quick mode selected by default (blue gradient background)
- ✅ Checkmark appears on selected card
- ✅ Clicking In-Depth card changes selection
- ✅ Info text updates based on selected mode
- ✅ Hover effects work (card lifts, shadow appears)
- ✅ Keyboard navigation works (Tab, Enter, Space)
- ✅ Responsive design works on mobile (cards stack vertically)

---

### **Test 7: Conditional Rendering**

**Objective:** Verify in-depth sections only appear for in-depth summaries

**Steps:**
1. Process video in Quick mode
2. Scroll through summary
3. Verify NO in-depth sections appear
4. Process SAME video in In-Depth mode
5. Scroll through summary
6. Verify in-depth sections appear AFTER full summary

**Expected Results:**
- ✅ Quick mode: No "In-Depth Analysis" badge or sections
- ✅ In-Depth mode: Visual divider with badge appears
- ✅ In-Depth mode: Three sections appear in order:
  1. Detailed Analysis
  2. Key Quotes
  3. Arguments & Claims
- ✅ Sections are properly styled with icons and colors

---

### **Test 8: Error Handling**

**Objective:** Verify error handling for invalid inputs

**Test Cases:**

**8.1: Invalid Mode Parameter**
```bash
# Direct API call with invalid mode
curl -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=test", "mode": "invalid"}'
```
**Expected:** 400 error with message "mode must be either 'quick' or 'indepth'"

**8.2: Missing Mode Parameter**
```bash
# API call without mode (should default to "quick")
curl -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=test"}'
```
**Expected:** Defaults to Quick mode, processes normally

**8.3: Invalid Video URL**
- Enter invalid URL in both modes
- Verify error message appears
- Verify mode selection persists after error

---

### **Test 9: Processing Indicator**

**Objective:** Verify processing indicator shows mode

**Steps:**
1. Enter video URL
2. Select Quick mode
3. Click "Generate Summary"
4. Observe button text
5. Cancel/wait for completion
6. Select In-Depth mode
7. Click "Generate Summary"
8. Observe button text

**Expected Results:**
- ✅ Quick mode: Button shows "Processing Video (Quick)..."
- ✅ In-Depth mode: Button shows "Processing Video (In-Depth)..."
- ✅ Spinner animation appears
- ✅ Button is disabled during processing

---

### **Test 10: Responsive Design**

**Objective:** Verify responsive design works on different screen sizes

**Steps:**
1. Open application on desktop (>1024px)
2. Verify mode selector shows two cards side-by-side
3. Resize browser to tablet (768px)
4. Verify mode selector still shows two cards
5. Resize browser to mobile (375px)
6. Verify mode selector stacks cards vertically

**Expected Results:**
- ✅ Desktop: Two cards side-by-side
- ✅ Tablet: Two cards side-by-side (slightly smaller)
- ✅ Mobile: Cards stack vertically
- ✅ All text remains readable
- ✅ Touch targets are large enough (min 44px)

---

## 🔍 Backend Verification Commands

### Check Mode Configuration
```bash
cd youtube-summarizer
source venv/bin/activate
python3 -c "
from src.services.ai_summarizer import AISummarizer
ai = AISummarizer()
print('Quick config:', ai.mode_configs['quick'])
print('Indepth config:', ai.mode_configs['indepth'])
"
```

### Monitor Logs During Testing
```bash
# In one terminal, tail the logs
cd youtube-summarizer
source venv/bin/activate
python3 src/main.py

# Watch for:
# - Mode selection logs
# - Chunking decision logs
# - Cache hit/miss logs
# - Processing time logs
```

---

## 📊 Success Criteria

### Functional Requirements
- ✅ Both modes process videos successfully
- ✅ Mode-specific configurations are applied correctly
- ✅ Chunking thresholds work as expected
- ✅ Independent caching works for each mode
- ✅ Conditional rendering shows/hides in-depth sections

### Performance Requirements
- ✅ Quick mode: <60 seconds for videos under 60 minutes
- ✅ In-Depth mode: <120 seconds for videos under 30 minutes
- ✅ Cached results: <1 second response time

### UI/UX Requirements
- ✅ Mode selector is intuitive and accessible
- ✅ Visual feedback for selected mode
- ✅ In-depth sections are visually distinct
- ✅ Responsive design works on all screen sizes

### Error Handling Requirements
- ✅ Invalid mode parameter returns 400 error
- ✅ Missing mode parameter defaults to "quick"
- ✅ Error messages are clear and helpful

---

## 🐛 Known Issues / Edge Cases

### To Test
- [ ] Very long videos (>2 hours) in In-Depth mode
- [ ] Videos with no transcript available
- [ ] Videos with multiple languages
- [ ] Rapid mode switching during processing
- [ ] Browser back button during processing

---

## 📝 Test Results Template

```markdown
## Test Results - [Date]

**Tester:** [Name]
**Environment:** [Local/Staging/Production]

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Quick Mode - Short Video | ✅ PASS | |
| 2 | In-Depth Mode - Short Video | ✅ PASS | |
| 3 | Quick Mode - Long Video | ✅ PASS | |
| 4 | In-Depth Mode - Long Video | ✅ PASS | |
| 5 | Independent Caching | ✅ PASS | |
| 6 | Mode Selector UI/UX | ✅ PASS | |
| 7 | Conditional Rendering | ✅ PASS | |
| 8 | Error Handling | ✅ PASS | |
| 9 | Processing Indicator | ✅ PASS | |
| 10 | Responsive Design | ✅ PASS | |

**Overall Status:** ✅ ALL TESTS PASSED

**Issues Found:** None

**Recommendations:** Ready for deployment
```

---

## ✅ Ready for Testing!

All implementation is complete. Follow this test plan to verify the dual-mode summarization feature works correctly before deployment.

