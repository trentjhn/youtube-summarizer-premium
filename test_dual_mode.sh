#!/bin/bash

# Dual-Mode Summarization Test Script
# Tests both Quick and In-Depth modes with a short video

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║              🧪 DUAL-MODE SUMMARIZATION FEATURE TEST                      ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Testing both Quick and In-Depth modes with a short video..."
echo ""

# Test video: Rick Astley - Never Gonna Give You Up (3:32)
TEST_VIDEO="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Quick Mode - Short Video"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Video: Rick Astley - Never Gonna Give You Up (3:32)"
echo "Mode: Quick Summary"
echo "Expected: 5 JSON components, no in-depth sections"
echo ""
echo "Processing..."
echo ""

# Make API call for Quick mode
QUICK_RESPONSE=$(curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"quick\"}")

# Parse and display results
echo "$QUICK_RESPONSE" | python3 << 'PYTHON_SCRIPT'
import sys, json

try:
    data = json.load(sys.stdin)
    
    if 'error' in data:
        print(f'❌ ERROR: {data["error"]}\n')
        sys.exit(1)
    
    summary = data.get('summary', {})
    
    print('✅ SUCCESS - Quick Mode Test\n')
    print(f'Video Title: {data.get("title", "N/A")}')
    print(f'Video ID: {data.get("video_id", "N/A")}')
    
    print('\n📊 JSON Components Found:')
    components = ['quick_takeaway', 'key_points', 'topics', 'timestamps', 'full_summary']
    all_present = True
    for comp in components:
        status = '✓' if comp in summary else '✗'
        if comp not in summary:
            all_present = False
        print(f'  {status} {comp}')
    
    # Check for in-depth components (should NOT be present)
    print('\n🔍 In-Depth Components (should be absent):')
    indepth_components = ['detailed_analysis', 'key_quotes', 'arguments']
    none_present = True
    for comp in indepth_components:
        if comp in summary:
            status = '✗ PRESENT (ERROR!)'
            none_present = False
        else:
            status = '✓ Absent (correct)'
        print(f'  {status} {comp}')
    
    # Display counts
    if 'key_points' in summary:
        print(f'\n📝 Key Points Count: {len(summary["key_points"])}')
    if 'full_summary' in summary:
        print(f'📄 Full Summary Paragraphs: {len(summary["full_summary"])}')
    
    # Final verdict
    print('\n' + '━'*78)
    if all_present and none_present:
        print('✅ TEST 1 PASSED: Quick mode working correctly!')
    else:
        print('❌ TEST 1 FAILED: Component mismatch detected')
    print('━'*78 + '\n')
    
except Exception as e:
    print(f'\n❌ ERROR parsing response: {e}\n')
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "Waiting 3 seconds before next test..."
sleep 3
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: In-Depth Mode - Same Video"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Video: Rick Astley - Never Gonna Give You Up (3:32)"
echo "Mode: In-Depth Analysis"
echo "Expected: 8 JSON components, including in-depth sections"
echo ""
echo "Processing..."
echo ""

# Make API call for In-Depth mode
INDEPTH_RESPONSE=$(curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"indepth\"}")

# Parse and display results
echo "$INDEPTH_RESPONSE" | python3 << 'PYTHON_SCRIPT'
import sys, json

try:
    data = json.load(sys.stdin)
    
    if 'error' in data:
        print(f'❌ ERROR: {data["error"]}\n')
        sys.exit(1)
    
    summary = data.get('summary', {})
    
    print('✅ SUCCESS - In-Depth Mode Test\n')
    print(f'Video Title: {data.get("title", "N/A")}')
    print(f'Video ID: {data.get("video_id", "N/A")}')
    
    print('\n📊 Standard JSON Components:')
    components = ['quick_takeaway', 'key_points', 'topics', 'timestamps', 'full_summary']
    standard_present = True
    for comp in components:
        status = '✓' if comp in summary else '✗'
        if comp not in summary:
            standard_present = False
        print(f'  {status} {comp}')
    
    # Check for in-depth components (SHOULD be present)
    print('\n🔍 In-Depth Components (should be present):')
    indepth_components = ['detailed_analysis', 'key_quotes', 'arguments']
    indepth_present = True
    for comp in indepth_components:
        if comp in summary:
            status = '✓ Present (correct)'
            count = len(summary[comp]) if isinstance(summary[comp], list) else 'N/A'
            print(f'  {status} {comp} ({count} items)')
        else:
            status = '✗ Absent (ERROR!)'
            indepth_present = False
            print(f'  {status} {comp}')
    
    # Display counts
    if 'key_points' in summary:
        print(f'\n📝 Key Points Count: {len(summary["key_points"])}')
    if 'full_summary' in summary:
        print(f'📄 Full Summary Paragraphs: {len(summary["full_summary"])}')
    
    # Final verdict
    print('\n' + '━'*78)
    if standard_present and indepth_present:
        print('✅ TEST 2 PASSED: In-Depth mode working correctly!')
    else:
        print('❌ TEST 2 FAILED: Component mismatch detected')
    print('━'*78 + '\n')
    
except Exception as e:
    print(f'\n❌ ERROR parsing response: {e}\n')
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Mode Parameter Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Testing invalid mode parameter..."
echo ""

# Test invalid mode
INVALID_RESPONSE=$(curl -s -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$TEST_VIDEO\", \"mode\": \"invalid\"}")

echo "$INVALID_RESPONSE" | python3 << 'PYTHON_SCRIPT'
import sys, json

try:
    data = json.load(sys.stdin)
    
    if 'error' in data:
        if 'quick' in data['error'] and 'indepth' in data['error']:
            print('✅ TEST 3 PASSED: Invalid mode rejected correctly!')
            print(f'   Error message: {data["error"]}\n')
        else:
            print(f'❌ TEST 3 FAILED: Unexpected error message: {data["error"]}\n')
    else:
        print('❌ TEST 3 FAILED: Invalid mode was accepted (should have been rejected)\n')
    
except Exception as e:
    print(f'\n❌ ERROR parsing response: {e}\n')
PYTHON_SCRIPT

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                    🎉 TESTING COMPLETE!                                   ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Quick Mode: Tested with 5 standard components"
echo "  • In-Depth Mode: Tested with 8 components (3 additional)"
echo "  • Validation: Tested invalid mode rejection"
echo ""
echo "Next Steps:"
echo "  1. Check the browser at http://localhost:5173"
echo "  2. Test the mode selector UI manually"
echo "  3. Verify conditional rendering of in-depth sections"
echo ""

