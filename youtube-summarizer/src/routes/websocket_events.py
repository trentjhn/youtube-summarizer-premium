"""
WebSocket Events - Real-time communication for progress updates

Provides WebSocket endpoints for real-time progress tracking during video processing.
Uses Flask-SocketIO for WebSocket support.
"""

import logging
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from src.services.progress_tracker import progress_tracker

logger = logging.getLogger(__name__)

# Will be initialized in main.py
socketio = None


def init_websocket(app):
    """
    Initialize WebSocket support for the Flask app.
    
    Args:
        app: Flask application instance
    """
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",  # Configure for production
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('response', {'data': 'Connected to progress tracker'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('subscribe_progress')
    def handle_subscribe_progress(data):
        """
        Subscribe to progress updates for a specific video.
        
        Args:
            data: Dictionary with 'video_id' key
        """
        video_id = data.get('video_id')
        if not video_id:
            emit('error', {'message': 'video_id is required'})
            return
        
        # Join a room for this video
        room = f"video_{video_id}"
        join_room(room)
        logger.info(f"Client {request.sid} subscribed to {room}")
        
        # Send current progress if available
        progress = progress_tracker.get_progress(video_id)
        if progress:
            emit('progress_update', progress.to_dict())
        else:
            emit('progress_update', {
                'video_id': video_id,
                'stage': 'queued',
                'progress_percent': 0,
                'message': 'Waiting to start processing...',
                'timestamp': None
            })
    
    @socketio.on('unsubscribe_progress')
    def handle_unsubscribe_progress(data):
        """
        Unsubscribe from progress updates for a specific video.
        
        Args:
            data: Dictionary with 'video_id' key
        """
        video_id = data.get('video_id')
        if not video_id:
            return
        
        room = f"video_{video_id}"
        leave_room(room)
        logger.info(f"Client {request.sid} unsubscribed from {room}")
    
    return socketio


def emit_progress_update(video_id: str, progress_update) -> None:
    """
    Emit progress update to all subscribed clients.
    
    Args:
        video_id: YouTube video ID
        progress_update: ProgressUpdate object
    """
    if not socketio:
        logger.warning("SocketIO not initialized")
        return
    
    room = f"video_{video_id}"
    socketio.emit(
        'progress_update',
        progress_update.to_dict(),
        room=room
    )
    logger.debug(f"Emitted progress update for {video_id}")


def emit_error(video_id: str, error_message: str) -> None:
    """
    Emit error message to all subscribed clients.
    
    Args:
        video_id: YouTube video ID
        error_message: Error message
    """
    if not socketio:
        logger.warning("SocketIO not initialized")
        return
    
    room = f"video_{video_id}"
    socketio.emit(
        'error',
        {'video_id': video_id, 'message': error_message},
        room=room
    )
    logger.debug(f"Emitted error for {video_id}: {error_message}")

