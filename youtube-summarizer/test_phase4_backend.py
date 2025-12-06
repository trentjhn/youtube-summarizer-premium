"""
Test script for Phase 4 backend implementation
Tests timestamp slicing and tone parameter functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.ai_summarizer import AISummarizer

def test_parse_timestamp():
    """Test timestamp parsing function"""
    print("\n=== Testing _parse_timestamp() ===")
    
    summarizer = AISummarizer()
    
    test_cases = [
        ("00:00", 0.0),
        ("01:30", 90.0),
        ("10:45", 645.0),
        ("1:05:30", 3930.0),
        ("end", -1),
    ]
    
    for timestamp_str, expected in test_cases:
        try:
            result = summarizer._parse_timestamp(timestamp_str)
            status = "✅" if result == expected else "❌"
            print(f"{status} {timestamp_str} -> {result} (expected: {expected})")
        except Exception as e:
            print(f"❌ {timestamp_str} -> ERROR: {e}")

def test_slice_transcript():
    """Test transcript slicing function"""
    print("\n=== Testing _slice_transcript() ===")
    
    summarizer = AISummarizer()
    
    # Create mock transcript data
    raw_segments = [
        {"start": 0.0, "end": 5.0, "text": "Hello and welcome to this video."},
        {"start": 5.0, "end": 10.0, "text": "Today we're going to talk about AI."},
        {"start": 10.0, "end": 15.0, "text": "AI is transforming the world."},
        {"start": 15.0, "end": 20.0, "text": "Let's explore some examples."},
        {"start": 20.0, "end": 25.0, "text": "First, we have natural language processing."},
        {"start": 25.0, "end": 30.0, "text": "Second, we have computer vision."},
        {"start": 30.0, "end": 35.0, "text": "Third, we have robotics."},
        {"start": 35.0, "end": 40.0, "text": "These are just a few applications."},
        {"start": 40.0, "end": 45.0, "text": "AI will continue to evolve."},
        {"start": 45.0, "end": 50.0, "text": "Thank you for watching."},
        {"start": 50.0, "end": 55.0, "text": "Please subscribe for more content."},
        {"start": 55.0, "end": 60.0, "text": "See you next time."},
        {"start": 60.0, "end": 65.0, "text": "Goodbye!"},
        {"start": 65.0, "end": 70.0, "text": "Extra content here."},
        {"start": 70.0, "end": 75.0, "text": "More extra content."},
        {"start": 75.0, "end": 80.0, "text": "Even more content."},
        {"start": 80.0, "end": 85.0, "text": "Still going."},
        {"start": 85.0, "end": 90.0, "text": "Almost done."},
        {"start": 90.0, "end": 95.0, "text": "Final segment."},
        {"start": 95.0, "end": 100.0, "text": "The end."},
    ]
    
    test_cases = [
        # (start_time, end_time, should_succeed, description)
        ("00:00", "01:00", True, "First 60 seconds (minimum valid)"),
        ("00:10", "01:20", True, "10 seconds to 1 min 20 sec (70 seconds)"),
        ("00:00", "end", True, "Full video"),
        ("00:30", "end", True, "From 30 seconds to end"),
        ("00:00", "00:30", False, "Only 30 seconds (below 60-second minimum)"),
        ("01:00", "00:30", False, "Start > End (invalid)"),
        ("05:00", "end", False, "Start beyond video length"),
    ]
    
    for start_time, end_time, should_succeed, description in test_cases:
        try:
            result = summarizer._slice_transcript(raw_segments, start_time, end_time)
            if should_succeed:
                print(f"✅ {description}")
                print(f"   Segment: {start_time} to {end_time}")
                print(f"   Result length: {len(result)} chars")
                print(f"   Preview: {result[:100]}...")
            else:
                print(f"❌ {description} - Expected error but succeeded")
        except ValueError as e:
            if not should_succeed:
                print(f"✅ {description}")
                print(f"   Correctly raised error: {str(e)[:80]}")
            else:
                print(f"❌ {description} - Unexpected error: {e}")
        except Exception as e:
            print(f"❌ {description} - Unexpected exception: {e}")

def test_tone_parameter():
    """Test that tone parameter is accepted"""
    print("\n=== Testing Tone Parameter ===")
    
    summarizer = AISummarizer()
    
    # Test that method signature accepts tone parameter
    try:
        # We won't actually call OpenAI, just verify the signature
        import inspect
        sig = inspect.signature(summarizer.generate_comprehensive_summary)
        params = list(sig.parameters.keys())
        
        expected_params = ['transcript', 'title', 'mode', 'raw_segments', 'start_time', 'end_time', 'tone']
        
        print(f"Method parameters: {params}")
        
        for param in expected_params:
            if param in params:
                print(f"✅ Parameter '{param}' exists")
            else:
                print(f"❌ Parameter '{param}' missing")
                
    except Exception as e:
        print(f"❌ Error inspecting method: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 4 BACKEND TESTING")
    print("=" * 60)
    
    test_parse_timestamp()
    test_slice_transcript()
    test_tone_parameter()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

