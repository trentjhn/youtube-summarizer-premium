"""
Unit tests for backend services

Tests for transcript extraction, AI summarization, and caching services.

NOTE (February 2026): The AI summarizer has been updated to use Google Gemini 2.5 Flash-Lite
instead of OpenAI GPT-4o-mini. The tests are designed to be API-agnostic, testing the
interface and behavior rather than the specific API implementation.

Model: Gemini 2.5 Flash-Lite
- 1M token context window
- $0.10 input / $0.40 output per 1M tokens
- API Key: GOOGLE_AI_API_KEY or GEMINI_API_KEY environment variable
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.transcript_extractor import TranscriptExtractor
from src.services.ai_summarizer import AISummarizer
from src.services.cache_manager import CacheManager


class TestTranscriptExtractor:
    """Tests for TranscriptExtractor service."""
    
    @pytest.fixture
    def mock_cache(self):
        """Create a mock cache manager."""
        return Mock(spec=CacheManager)
    
    @pytest.fixture
    def extractor(self, mock_cache):
        """Create a TranscriptExtractor instance with mock cache."""
        return TranscriptExtractor(mock_cache)
    
    def test_extract_video_id_standard_url(self, extractor):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self, extractor):
        """Test extracting video ID from shortened YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self, extractor):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_timestamp(self, extractor):
        """Test extracting video ID from URL with timestamp."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123s"
        video_id = extractor.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self, extractor):
        """Test that invalid URL raises ValueError."""
        url = "https://example.com/video"
        with pytest.raises(ValueError):
            extractor.extract_video_id(url)
    
    def test_clean_transcript_text(self, extractor):
        """Test transcript text cleaning."""
        dirty_text = "[Music] Hello (inaudible) world  [Applause]"
        clean_text = extractor._clean_transcript_text(dirty_text)
        assert "[Music]" not in clean_text
        assert "[Applause]" not in clean_text
        assert "(inaudible)" not in clean_text
        assert "  " not in clean_text  # No double spaces


class TestAISummarizer:
    """
    Tests for AISummarizer service.

    The summarizer uses Google Gemini 2.5 Flash-Lite for AI-powered summarization.
    These tests verify the interface and caching behavior without requiring API calls.
    """

    @pytest.fixture
    def mock_cache(self):
        """Create a mock cache manager."""
        return Mock(spec=CacheManager)

    @pytest.fixture
    def summarizer(self, mock_cache):
        """Create an AISummarizer instance with mock cache."""
        return AISummarizer(mock_cache)

    def test_summarizer_initialization(self, summarizer):
        """Test that summarizer initializes correctly with Gemini model config."""
        assert summarizer.cache is not None
        assert summarizer.system_prompt is not None
        # Verify mode configs exist for dual-mode summarization
        assert "quick" in summarizer.mode_configs
        assert "indepth" in summarizer.mode_configs

    def test_mode_configs_have_updated_thresholds(self, summarizer):
        """Test that chunking thresholds are updated for 1M context window."""
        # With Gemini's 1M context, thresholds should be much higher than before
        # Old thresholds were 60 min (quick) and 30 min (indepth)
        # New thresholds should be 420 min (~7 hours) for both
        assert summarizer.mode_configs["quick"]["chunking_threshold"] >= 400
        assert summarizer.mode_configs["indepth"]["chunking_threshold"] >= 400

    def test_empty_transcript_raises_error(self, summarizer):
        """Test that empty transcript raises ValueError."""
        with pytest.raises(ValueError):
            summarizer.generate_comprehensive_summary("", "Test Video")

    def test_cache_hit_returns_cached_summary(self, summarizer, mock_cache):
        """Test that cached JSON summary is returned without API call."""
        transcript = "This is a test transcript"
        title = "Test Video"
        # The summarizer now returns JSON structures, not strings
        cached_summary = {
            "quick_takeaway": "Test takeaway",
            "key_points": ["Point 1", "Point 2"],
            "topics": [{"topic_name": "Topic 1", "summary_section_id": 1}],
            "timestamps": [],
            "full_summary": [{"id": 1, "content": "Test summary content"}]
        }

        # Setup mock cache
        mock_cache.generate_content_hash.return_value = "hash123"
        mock_cache.get_cached_summary.return_value = cached_summary

        result = summarizer.generate_comprehensive_summary(transcript, title)

        assert result == cached_summary
        mock_cache.get_cached_summary.assert_called_once()

    def test_fallback_summary_structure(self, summarizer):
        """Test that fallback summary returns valid JSON structure."""
        transcript = "This is a test transcript for fallback"
        title = "Test Video"

        # Call the fallback method directly
        fallback = summarizer._get_fallback_summary(transcript, title)

        # Verify it returns a valid JSON structure
        assert "quick_takeaway" in fallback
        assert "key_points" in fallback
        assert "full_summary" in fallback
        assert isinstance(fallback["key_points"], list)
        assert isinstance(fallback["full_summary"], list)


class TestCacheManager:
    """Tests for CacheManager service."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        mock = Mock()
        mock.ping.return_value = True
        return mock
    
    @pytest.fixture
    def cache_manager(self, mock_redis):
        """Create a CacheManager instance with mock Redis."""
        return CacheManager(mock_redis)
    
    def test_cache_manager_initialization(self, cache_manager):
        """Test that cache manager initializes correctly."""
        assert cache_manager.redis is not None
        assert cache_manager.default_ttl == 3600
    
    def test_generate_content_hash(self, cache_manager):
        """Test content hash generation."""
        content = "Test content"
        hash1 = cache_manager.generate_content_hash(content)
        hash2 = cache_manager.generate_content_hash(content)
        
        # Same content should produce same hash
        assert hash1 == hash2
        # Hash should be 16 characters
        assert len(hash1) == 16
    
    def test_cache_transcript(self, cache_manager, mock_redis):
        """Test caching transcript data."""
        video_id = "test123"
        transcript_data = {"transcript": "Test", "title": "Test Video"}
        
        mock_redis.setex.return_value = True
        
        result = cache_manager.cache_transcript(video_id, transcript_data)
        
        assert result is True
        mock_redis.setex.assert_called_once()
    
    def test_get_cached_transcript(self, cache_manager, mock_redis):
        """Test retrieving cached transcript."""
        video_id = "test123"
        cached_data = '{"transcript": "Test", "title": "Test Video"}'
        
        mock_redis.get.return_value = cached_data
        
        result = cache_manager.get_cached_transcript(video_id)
        
        assert result["transcript"] == "Test"
        assert result["title"] == "Test Video"

