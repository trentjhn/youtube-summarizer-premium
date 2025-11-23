"""
Video Routes - API endpoints for video processing

This module defines the Flask blueprint for video-related API endpoints.
Implements the core MVP functionality: processing YouTube video URLs
into comprehensive summaries.
"""

import logging
from flask import Blueprint, request, jsonify
from src.models.video import db, Video
from src.services.transcript_extractor import TranscriptExtractor
from src.services.ai_summarizer import AISummarizer
from src.services.cache_manager import CacheManager
from src.services.data_extractor import DataExtractor
from src.services.chat_service import ChatService
from src.utils.error_handler import (
    handle_api_error,
    InvalidURLError,
    TranscriptExtractionError,
    AIProcessingError,
    retry_with_backoff
)
from src.middleware import limit_video_processing
import redis

# Import limiter from main app (will be set after app creation)
limiter = None

# Configure logging
logger = logging.getLogger(__name__)

# Create Flask blueprint for video routes
video_bp = Blueprint('video', __name__)

# Initialize services
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    cache_manager = CacheManager(redis_client)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Caching disabled.")
    cache_manager = CacheManager(None)

transcript_extractor = TranscriptExtractor(cache_manager)
ai_summarizer = AISummarizer(cache_manager)
data_extractor = DataExtractor()
chat_service = ChatService()

@video_bp.route('/process-video', methods=['POST'])
@handle_api_error
def process_video():
    """
    Process a YouTube video URL and generate comprehensive summary.

    Endpoint: POST /api/process-video
    Request body: {"video_url": "https://youtube.com/watch?v=..."}

    Returns:
        JSON with video data including title, transcript, and summary
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        video_url = data.get('video_url')
        if not video_url:
            return jsonify({'error': 'video_url is required'}), 400

        logger.info(f"Processing video URL: {video_url}")

        # Extract video ID from URL
        try:
            video_id = transcript_extractor.extract_video_id(video_url)
        except ValueError as e:
            logger.warning(f"Invalid URL provided: {video_url}")
            raise InvalidURLError(f'Invalid YouTube URL: {str(e)}')

        # Check if video already exists and is completed
        existing_video = Video.query.filter_by(video_id=video_id).first()
        if existing_video and existing_video.status == 'completed':
            logger.info(f"Video {video_id} already processed, returning cached result")
            return jsonify(existing_video.to_dict())

        # Create or update video record
        if not existing_video:
            video = Video(video_id=video_id, url=video_url, title="Processing...", status='processing')
            db.session.add(video)
        else:
            video = existing_video
            video.status = 'processing'

        db.session.commit()

        try:
            # Extract transcript with retry logic
            logger.info(f"Extracting transcript for video {video_id}")
            transcript_data = transcript_extractor.get_transcript(video_id)
            video.title = transcript_data.get('title', f'Video {video_id}')
            video.transcript = transcript_data.get('transcript')

            if not video.transcript or not video.transcript.strip():
                raise TranscriptExtractionError("No transcript available for this video")

            logger.info(f"Transcript extracted successfully ({len(video.transcript)} chars)")
            logger.info(f"DEBUG: Extracted title: '{video.title}'")
            logger.info(f"DEBUG: Transcript first 300 chars: {video.transcript[:300]}")
            logger.info(f"DEBUG: Transcript extraction method: {transcript_data.get('method', 'unknown')}")
            logger.info(f"DEBUG: Is auto-generated: {transcript_data.get('is_auto_generated', 'unknown')}")

            # Generate AI summary
            logger.info(f"Generating AI summary for '{video.title}'")
            summary = ai_summarizer.generate_comprehensive_summary(video.transcript, video.title)
            video.summary = summary
            video.status = 'completed'

            db.session.commit()
            logger.info(f"Video {video_id} processed successfully")
            return jsonify(video.to_dict())

        except TranscriptExtractionError as e:
            logger.error(f"Transcript extraction failed for {video_id}: {e}")
            video.status = 'failed'
            db.session.commit()
            raise
        except Exception as processing_error:
            logger.error(f"Processing failed for {video_id}: {processing_error}")
            video.status = 'failed'
            db.session.commit()
            raise AIProcessingError(f'Processing failed: {str(processing_error)}')

    except Exception as e:
        logger.error(f"Unexpected error in process_video: {e}", exc_info=True)
        raise


@video_bp.route('/video/<video_id>/structured', methods=['GET'])
@handle_api_error
def get_structured_data(video_id: str) -> tuple:
    """
    Extract and return structured data from a video's AI-generated summary.

    Endpoint: GET /api/video/<video_id>/structured

    This endpoint retrieves a video's AI-generated summary and extracts
    structured data including executive summary, key metrics, key points,
    action items, and timestamps. Works with any YouTube video genre.

    Args:
        video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")

    Returns:
        JSON response with structured data:
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Video Title",
            "structured_data": {
                "executive_summary": "30-second takeaway",
                "key_metrics": [
                    {"name": "metric", "value": "123", "type": "numeric"}
                ],
                "key_points": ["Point 1", "Point 2"],
                "action_items": ["Action 1", "Action 2"],
                "timestamps": [
                    {"time": "1:23", "topic": "Topic", "key_point": "..."}
                ]
            }
        }

    Status Codes:
        200: Successfully extracted structured data
        404: Video not found or summary not available
        500: Extraction error

    Raises:
        VideoProcessingError: If extraction fails
    """
    try:
        # Validate video_id format
        if not video_id or not isinstance(video_id, str) or len(video_id) == 0:
            logger.warning(f"Invalid video_id format: {video_id}")
            return jsonify({
                'error': 'Invalid video ID format',
                'error_type': 'invalid_video_id'
            }), 400

        logger.info(f"Retrieving structured data for video: {video_id}")

        # Query video from database
        video = Video.query.filter_by(video_id=video_id).first()

        if not video:
            logger.warning(f"Video not found: {video_id}")
            return jsonify({
                'error': f'Video with ID "{video_id}" not found',
                'error_type': 'video_not_found'
            }), 404

        # Check if video has been processed and has a summary
        if video.status != 'completed':
            logger.warning(f"Video {video_id} not completed. Status: {video.status}")
            return jsonify({
                'error': f'Video processing not completed. Current status: {video.status}',
                'error_type': 'video_not_ready'
            }), 404

        if not video.summary or not video.summary.strip():
            logger.warning(f"Video {video_id} has no summary available")
            return jsonify({
                'error': 'No summary available for this video',
                'error_type': 'no_summary'
            }), 404

        # Extract structured data from summary
        logger.info(f"Extracting structured data from summary for {video_id}")
        structured_data = data_extractor.extract(video.summary, video.title)

        # Build response
        response = {
            'video_id': video.video_id,
            'title': video.title,
            'structured_data': structured_data
        }

        logger.info(f"Successfully extracted structured data for {video_id}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unexpected error in get_structured_data: {e}", exc_info=True)
        raise


@video_bp.route('/chat', methods=['POST'])
@handle_api_error
def chat():
    """
    AI chat endpoint for context-aware video Q&A.

    Allows users to ask questions about a video's content. The AI uses the
    video's summary and transcript to provide accurate, contextual responses.

    Request Body:
        {
            "video_id": "string (required) - YouTube video ID",
            "message": "string (required) - User's question/message",
            "conversation_history": [  // optional
                {"role": "user", "content": "previous question"},
                {"role": "assistant", "content": "previous response"}
            ]
        }

    Returns:
        200: {
            "success": true,
            "response": "AI response text",
            "video_id": "video_id"
        }
        400: Invalid request (missing fields, message too long, etc.)
        404: Video not found
        500: Server error

    Safety Guardrails:
        - Validates video_id exists in database
        - Sanitizes user input
        - Limits message length (500 chars)
        - Limits conversation history (10 messages)
        - Graceful error handling
    """
    try:
        # Parse request body
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400

        # Validate required fields
        video_id = data.get('video_id')
        message = data.get('message')

        if not video_id:
            return jsonify({
                'success': False,
                'error': 'video_id is required'
            }), 400

        if not message:
            return jsonify({
                'success': False,
                'error': 'message is required'
            }), 400

        # Get conversation history (optional)
        conversation_history = data.get('conversation_history', [])

        # Validate conversation history format
        if not isinstance(conversation_history, list):
            return jsonify({
                'success': False,
                'error': 'conversation_history must be an array'
            }), 400

        logger.info(f"Chat request for video {video_id}: {message[:50]}...")

        # Fetch video from database
        video = Video.query.filter_by(video_id=video_id).first()

        if not video:
            logger.warning(f"Video not found: {video_id}")
            return jsonify({
                'success': False,
                'error': f'Video not found: {video_id}'
            }), 404

        # Validate video has summary and transcript
        if not video.summary:
            logger.warning(f"Video {video_id} has no summary")
            return jsonify({
                'success': False,
                'error': 'Video has not been processed yet. Please process the video first.'
            }), 400

        if not video.transcript:
            logger.warning(f"Video {video_id} has no transcript")
            return jsonify({
                'success': False,
                'error': 'Video transcript not available'
            }), 400

        # Ensure summary is in JSON format
        summary = video.summary
        if isinstance(summary, str):
            logger.warning(f"Video {video_id} has text summary, not JSON. Chat may be less effective.")
            # Create minimal JSON structure from text summary
            summary = {
                'quick_takeaway': 'Summary available in text format',
                'key_points': [],
                'topics': [],
                'timestamps': [],
                'full_summary': [{'id': 1, 'content': summary}]
            }

        # Generate chat response using ChatService
        try:
            result = chat_service.chat(
                message=message,
                video_title=video.title,
                summary=summary,
                transcript=video.transcript,
                conversation_history=conversation_history
            )

            # Check if there was an error in chat generation
            if result.get('error'):
                logger.error(f"Chat service error: {result['error']}")
                # Still return the fallback response

            response = {
                'success': True,
                'response': result['response'],
                'video_id': video_id
            }

            logger.info(f"Successfully generated chat response for video {video_id}")
            return jsonify(response), 200

        except ValueError as e:
            # Validation errors (message too long, empty, etc.)
            logger.warning(f"Chat validation error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

        except Exception as e:
            # Unexpected errors in chat service
            logger.error(f"Chat service failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Failed to generate chat response. Please try again.'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

