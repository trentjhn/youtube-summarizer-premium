"""
Integration tests for API endpoints

Tests for video processing API endpoints with mocked external services.
"""

import pytest
import json
from unittest.mock import patch, Mock
from src.main import app
from src.models.video import db, Video


@pytest.fixture
def client():
    """Create a test client with in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_video_url():
    """Sample YouTube URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class TestProcessVideoEndpoint:
    """Tests for /api/process-video endpoint."""
    
    def test_missing_video_url(self, client):
        """Test that missing video_url returns 400 error."""
        response = client.post(
            '/api/process-video',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_invalid_json(self, client):
        """Test that invalid JSON returns 400 error."""
        response = client.post(
            '/api/process-video',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_invalid_youtube_url(self, client):
        """Test that invalid YouTube URL returns 400 error."""
        response = client.post(
            '/api/process-video',
            data=json.dumps({'video_url': 'https://example.com'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('src.services.transcript_extractor.TranscriptExtractor.get_transcript')
    @patch('src.services.ai_summarizer.AISummarizer.generate_comprehensive_summary')
    def test_successful_video_processing(
        self,
        mock_summary,
        mock_transcript,
        client,
        sample_video_url
    ):
        """Test successful video processing."""
        # Mock external services
        mock_transcript.return_value = {
            'title': 'Test Video Title',
            'transcript': 'This is a test transcript with meaningful content.',
            'method': 'youtube_api',
            'language': 'en'
        }
        mock_summary.return_value = '# Test Video Title\n\n## Summary\nThis is a test summary.'
        
        response = client.post(
            '/api/process-video',
            data=json.dumps({'video_url': sample_video_url}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Test Video Title'
        assert data['status'] == 'completed'
        assert 'summary' in data
        assert 'transcript' in data
    
    @patch('src.services.transcript_extractor.TranscriptExtractor.get_transcript')
    def test_transcript_extraction_failure(self, mock_transcript, client, sample_video_url):
        """Test handling of transcript extraction failure."""
        mock_transcript.side_effect = Exception("Transcript extraction failed")
        
        response = client.post(
            '/api/process-video',
            data=json.dumps({'video_url': sample_video_url}),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('src.services.transcript_extractor.TranscriptExtractor.get_transcript')
    @patch('src.services.ai_summarizer.AISummarizer.generate_comprehensive_summary')
    def test_ai_processing_failure(
        self,
        mock_summary,
        mock_transcript,
        client,
        sample_video_url
    ):
        """Test handling of AI processing failure."""
        mock_transcript.return_value = {
            'title': 'Test Video',
            'transcript': 'Test transcript',
            'method': 'youtube_api',
            'language': 'en'
        }
        mock_summary.side_effect = Exception("AI processing failed")
        
        response = client.post(
            '/api/process-video',
            data=json.dumps({'video_url': sample_video_url}),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('src.services.transcript_extractor.TranscriptExtractor.get_transcript')
    @patch('src.services.ai_summarizer.AISummarizer.generate_comprehensive_summary')
    def test_cached_video_returns_immediately(
        self,
        mock_summary,
        mock_transcript,
        client,
        sample_video_url
    ):
        """Test that already processed videos are returned from cache."""
        # Mock external services
        mock_transcript.return_value = {
            'title': 'Test Video',
            'transcript': 'Test transcript',
            'method': 'youtube_api',
            'language': 'en'
        }
        mock_summary.return_value = '# Test Video\n\nSummary'
        
        # First request
        response1 = client.post(
            '/api/process-video',
            data=json.dumps({'video_url': sample_video_url}),
            content_type='application/json'
        )
        assert response1.status_code == 200
        
        # Reset mocks
        mock_transcript.reset_mock()
        mock_summary.reset_mock()
        
        # Second request should return cached result
        response2 = client.post(
            '/api/process-video',
            data=json.dumps({'video_url': sample_video_url}),
            content_type='application/json'
        )
        
        assert response2.status_code == 200
        # External services should not be called again
        mock_transcript.assert_not_called()
        mock_summary.assert_not_called()

