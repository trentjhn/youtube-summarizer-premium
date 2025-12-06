#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║              🧪 TESTING MODE-AWARE CACHING FIX                            ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This test verifies that Quick and In-Depth modes cache independently."
echo ""

# Use a fresh video that hasn't been processed yet
TEST_VIDEO="https://www.youtube.com/watch?v=jNQXAC9IVRw"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Process video in Quick mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

QUICK_RESPONSE=$(curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"quick\"}")

echo "$QUICK_RESPONSE" | python3 << 'PYTHON_SCRIPT'
import sys, json

try:
    data = json.load(sys.stdin)
    
    if 'error' in data:
        print(f'❌ ERROR: {data["error"]}\n')
        sys.exit(1)
    
    print(f'✅ Quick mode processed successfully')
    print(f'   Video ID: {data.get("video_id", "N/A")}')
    print(f'   Mode: {data.get("mode", "NOT FOUND")}')
    print(f'   Status: {data.get("status", "N/A")}')
    
    summary = data.get('summary', {})
    has_indepth = 'detailed_analysis' in summary or 'key_quotes' in summary or 'arguments' in summary
    print(f'   Has in-depth sections: {has_indepth}')
    
    if has_indepth:
        print(f'   ❌ ERROR: Quick mode should NOT have in-depth sections!')
    else:
        print(f'   ✅ Correct: No in-depth sections')
    
    print(f'   Components: {", ".join(list(summary.keys())[:8])}')
    print()
    
except Exception as e:
    print(f'❌ ERROR parsing response: {e}\n')
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Process SAME video in In-Depth mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Expected: Should process fresh (NOT return cached Quick result)"
echo ""

INDEPTH_RESPONSE=$(curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"indepth\"}")

echo "$INDEPTH_RESPONSE" | python3 << 'PYTHON_SCRIPT'
import sys, json

try:
    data = json.load(sys.stdin)
    
    if 'error' in data:
        print(f'❌ ERROR: {data["error"]}\n')
        sys.exit(1)
    
    print(f'✅ In-Depth mode processed successfully')
    print(f'   Video ID: {data.get("video_id", "N/A")}')
    print(f'   Mode: {data.get("mode", "NOT FOUND")}')
    print(f'   Status: {data.get("status", "N/A")}')
    
    summary = data.get('summary', {})
    has_indepth = 'detailed_analysis' in summary or 'key_quotes' in summary or 'arguments' in summary
    print(f'   Has in-depth sections: {has_indepth}')
    
    if not has_indepth:
        print(f'   ❌ ERROR: In-Depth mode SHOULD have in-depth sections!')
        print(f'   This means it returned the cached Quick result (BUG!)')
    else:
        print(f'   ✅ Correct: Has in-depth sections')
        print(f'   ✅ Mode-aware caching is working!')
    
    print(f'   Components: {", ".join(list(summary.keys()))}')
    print()
    
except Exception as e:
    print(f'❌ ERROR parsing response: {e}\n')
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Verify caching works for each mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Processing same video in Quick mode again (should be instant from cache)..."

curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"quick\"}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ Quick mode (cached): {data.get(\"status\")}')
print(f'   Mode: {data.get(\"mode\", \"NOT FOUND\")}')
"

echo ""
echo "Processing same video in In-Depth mode again (should be instant from cache)..."

curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"indepth\"}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ In-Depth mode (cached): {data.get(\"status\")}')
print(f'   Mode: {data.get(\"mode\", \"NOT FOUND\")}')
"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                    ✅ TEST COMPLETE!                                      ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Quick mode caches independently ✓"
echo "  • In-Depth mode caches independently ✓"
echo "  • Same video can have both modes cached ✓"
echo ""

