"""
Tests Package - Comprehensive test suite for YouTube Video Summarizer

This package contains all tests for the application, organized by component:

- test_models.py: Database model tests
- test_services.py: Service layer tests (cache, transcript, AI)
- test_routes.py: API endpoint tests
- test_integration.py: End-to-end integration tests

Testing Strategy:
- Unit tests for individual components
- Integration tests for service interactions
- API tests for endpoint functionality
- Mock external dependencies (YouTube API, OpenAI API)

Run tests with: pytest tests/
"""

