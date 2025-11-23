"""
Unit tests for Video Routes - Structured Data Endpoint

Tests the GET /api/video/<video_id>/structured endpoint that extracts
structured data from AI-generated summaries using the DataExtractor service.
"""

import pytest
import json
from src.main import app
from src.models.video import db, Video
from src.services.data_extractor import DataExtractor


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
def sample_summary():
    """Sample AI-generated summary for testing."""
    return """
# Python Programming Fundamentals

## Overview
Learn Python basics with 50,000+ students worldwide. This comprehensive course covers
fundamentals in 40 hours with 95% completion rate and 4.8/5 star rating.

## Key Points
- Variables and data types (strings, integers, floats)
- Functions and modules for code reusability
- Object-oriented programming concepts
- Error handling and debugging techniques
- Real-world project examples

## Action Items
- Complete 40 hours of video content
- Practice with 20+ coding exercises
- Build 3 capstone projects
- Join community forum for support

## Timestamps
- 2:15 - Introduction to Python
- 5:30 - Variables and data types
- 12:45 - Functions and scope
- 25:00 - Object-oriented programming
"""


@pytest.fixture
def sample_video_with_summary(client, sample_summary):
    """Create a test video with completed status and summary."""
    video = Video(
        video_id='test_video_123',
        title='Python Programming Fundamentals',
        url='https://youtube.com/watch?v=test_video_123',
        transcript='Sample transcript content',
        summary=sample_summary,
        status='completed'
    )
    db.session.add(video)
    db.session.commit()
    yield video
    # Cleanup
    db.session.delete(video)
    db.session.commit()


@pytest.fixture
def sample_video_processing(client):
    """Create a test video with processing status."""
    video = Video(
        video_id='processing_video_456',
        title='Processing Video',
        url='https://youtube.com/watch?v=processing_video_456',
        transcript='Sample transcript',
        summary=None,
        status='processing'
    )
    db.session.add(video)
    db.session.commit()
    yield video
    # Cleanup
    db.session.delete(video)
    db.session.commit()


@pytest.fixture
def sample_video_no_summary(client):
    """Create a test video with completed status but no summary."""
    video = Video(
        video_id='no_summary_789',
        title='Video Without Summary',
        url='https://youtube.com/watch?v=no_summary_789',
        transcript='Sample transcript',
        summary=None,
        status='completed'
    )
    db.session.add(video)
    db.session.commit()
    yield video
    # Cleanup
    db.session.delete(video)
    db.session.commit()


class TestGetStructuredDataSuccess:
    """Test successful structured data extraction."""

    def test_extract_structured_data_success(self, client, sample_video_with_summary):
        """Test successful extraction of structured data."""
        response = client.get('/api/video/test_video_123/structured')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify response structure
        assert 'video_id' in data
        assert 'title' in data
        assert 'structured_data' in data
        
        # Verify video information
        assert data['video_id'] == 'test_video_123'
        assert data['title'] == 'Python Programming Fundamentals'
        
        # Verify structured data fields
        structured = data['structured_data']
        assert 'executive_summary' in structured
        assert 'key_metrics' in structured
        assert 'key_points' in structured
        assert 'action_items' in structured
        assert 'timestamps' in structured
        
        # Verify data types
        assert isinstance(structured['executive_summary'], str)
        assert isinstance(structured['key_metrics'], list)
        assert isinstance(structured['key_points'], list)
        assert isinstance(structured['action_items'], list)
        assert isinstance(structured['timestamps'], list)

    def test_extract_metrics_from_summary(self, client, sample_video_with_summary):
        """Test that metrics are correctly extracted."""
        response = client.get('/api/video/test_video_123/structured')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        metrics = data['structured_data']['key_metrics']
        
        # Should extract metrics like 50,000+, 40 hours, 95%, 4.8
        assert len(metrics) > 0
        
        # Verify metric structure
        for metric in metrics:
            assert 'name' in metric
            assert 'value' in metric
            assert 'type' in metric

    def test_extract_key_points_from_summary(self, client, sample_video_with_summary):
        """Test that key points are correctly extracted."""
        response = client.get('/api/video/test_video_123/structured')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        key_points = data['structured_data']['key_points']
        
        # Should extract key points from bullet list
        assert len(key_points) > 0
        assert all(isinstance(point, str) for point in key_points)

    def test_extract_action_items_from_summary(self, client, sample_video_with_summary):
        """Test that action items are correctly extracted."""
        response = client.get('/api/video/test_video_123/structured')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        action_items = data['structured_data']['action_items']
        
        # Should extract action items
        assert len(action_items) > 0
        assert all(isinstance(item, str) for item in action_items)

    def test_extract_timestamps_from_summary(self, client, sample_video_with_summary):
        """Test that timestamps are correctly extracted."""
        response = client.get('/api/video/test_video_123/structured')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        timestamps = data['structured_data']['timestamps']
        
        # Should extract timestamps
        assert len(timestamps) > 0
        
        # Verify timestamp structure
        for ts in timestamps:
            assert 'time' in ts
            assert 'topic' in ts


class TestGetStructuredDataErrors:
    """Test error handling for structured data endpoint."""

    def test_video_not_found(self, client):
        """Test 404 when video doesn't exist."""
        response = client.get('/api/video/nonexistent_video/structured')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error_type'] == 'video_not_found'

    def test_video_still_processing(self, client, sample_video_processing):
        """Test 404 when video is still processing."""
        response = client.get('/api/video/processing_video_456/structured')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error_type'] == 'video_not_ready'
        assert 'processing' in data['error'].lower()

    def test_video_no_summary(self, client, sample_video_no_summary):
        """Test 404 when video has no summary."""
        response = client.get('/api/video/no_summary_789/structured')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error_type'] == 'no_summary'

    def test_invalid_video_id_empty(self, client):
        """Test 400 with empty video ID."""
        response = client.get('/api/video//structured')
        
        # Flask routing will handle this, but test the pattern
        assert response.status_code in [404, 400]

    def test_response_format_consistency(self, client, sample_video_with_summary):
        """Test that response format is consistent."""
        response = client.get('/api/video/test_video_123/structured')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify all required fields are present
        required_fields = ['video_id', 'title', 'structured_data']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify structured_data has all required fields
        required_structured_fields = [
            'executive_summary',
            'key_metrics',
            'key_points',
            'action_items',
            'timestamps'
        ]
        for field in required_structured_fields:
            assert field in data['structured_data'], f"Missing structured field: {field}"


class TestGetStructuredDataIntegration:
    """Integration tests for structured data endpoint."""

    def test_multiple_videos_independent(self, client):
        """Test that multiple videos are handled independently."""
        # Create two different videos
        video1 = Video(
            video_id='video_1',
            title='Video 1',
            url='https://youtube.com/watch?v=video_1',
            transcript='Transcript 1',
            summary='# Video 1\n\n## Overview\nThis is video 1 with 100 views.',
            status='completed'
        )
        video2 = Video(
            video_id='video_2',
            title='Video 2',
            url='https://youtube.com/watch?v=video_2',
            transcript='Transcript 2',
            summary='# Video 2\n\n## Overview\nThis is video 2 with 200 views.',
            status='completed'
        )
        db.session.add(video1)
        db.session.add(video2)
        db.session.commit()

        try:
            # Get structured data for both videos
            response1 = client.get('/api/video/video_1/structured')
            response2 = client.get('/api/video/video_2/structured')

            assert response1.status_code == 200
            assert response2.status_code == 200

            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)

            # Verify they're different
            assert data1['video_id'] == 'video_1'
            assert data2['video_id'] == 'video_2'
            assert data1['title'] == 'Video 1'
            assert data2['title'] == 'Video 2'
        finally:
            # Cleanup
            db.session.delete(video1)
            db.session.delete(video2)
            db.session.commit()

    def test_endpoint_performance(self, client, sample_video_with_summary):
        """Test that endpoint responds quickly."""
        import time
        
        start = time.time()
        response = client.get('/api/video/test_video_123/structured')
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should respond in less than 1 second
        assert elapsed < 1.0, f"Endpoint took {elapsed}s, expected <1s"

