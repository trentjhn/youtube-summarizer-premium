#!/usr/bin/env python3
"""
Test script for yt-dlp transcript extraction.

This script tests the new yt-dlp extraction method to ensure it works correctly
before deploying to production.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.transcript_extractor import TranscriptExtractor
from services.cache_manager import CacheManager

def test_transcript_extraction():
    """Test transcript extraction with multiple videos."""
    
    print("=" * 80)
    print("Testing yt-dlp Transcript Extraction")
    print("=" * 80)
    print()
    
    # Initialize with a dummy cache manager
    cache_manager = CacheManager(redis_client=None)
    extractor = TranscriptExtractor(cache_manager)
    
    # Test videos with known transcripts
    test_videos = [
        ("m92GE57Rn7o", "Known video with transcript"),
        ("jNQXAC9IVRw", "Me at the zoo - First YouTube video"),
        ("dQw4w9WgXcQ", "Rick Astley - Never Gonna Give You Up"),
    ]
    
    results = []
    
    for video_id, description in test_videos:
        print(f"\n{'=' * 80}")
        print(f"Testing: {description}")
        print(f"Video ID: {video_id}")
        print(f"{'=' * 80}")
        
        try:
            result = extractor.get_transcript(video_id)
            
            print(f"✅ SUCCESS!")
            print(f"   Method: {result['method']}")
            print(f"   Title: {result['title']}")
            print(f"   Transcript Length: {len(result['transcript'])} characters")
            print(f"   Language: {result.get('language', 'unknown')}")
            print(f"   Preview: {result['transcript'][:200]}...")
            
            results.append({
                'video_id': video_id,
                'description': description,
                'success': True,
                'method': result['method'],
                'length': len(result['transcript'])
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                'video_id': video_id,
                'description': description,
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {(successful/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        if r['success']:
            print(f"  {status} {r['video_id']}: {r['method']} ({r['length']} chars)")
        else:
            print(f"  {status} {r['video_id']}: {r['error']}")
    
    print(f"\n{'=' * 80}")
    
    if successful == total:
        print("🎉 ALL TESTS PASSED! Transcript extraction is working correctly.")
        return 0
    elif successful > 0:
        print("⚠️  PARTIAL SUCCESS: Some tests passed, but not all.")
        return 1
    else:
        print("❌ ALL TESTS FAILED: Transcript extraction is not working.")
        return 2

if __name__ == "__main__":
    exit_code = test_transcript_extraction()
    sys.exit(exit_code)

