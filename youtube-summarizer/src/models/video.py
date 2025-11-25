"""
Video Model - Database schema for YouTube video processing

This module defines the SQLAlchemy model for storing YouTube video data,
transcripts, and AI-generated summaries. The model supports the MVP workflow
of processing individual video URLs into comprehensive summaries.

Key Design Decisions:
- video_id is unique to prevent duplicate processing
- status field enables tracking processing state and error recovery
- transcript and summary stored as TEXT for large content
- timestamps enable audit trail and cache invalidation
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemy instance - will be initialized with Flask app in main.py
db = SQLAlchemy()

class Video(db.Model):
    """
    Video model representing a YouTube video and its processing state.
    
    This model stores the complete lifecycle of video processing:
    1. Initial URL submission (pending status)
    2. Transcript extraction (processing status) 
    3. AI summarization (processing status)
    4. Final result (completed/failed status)
    
    The model is designed for the MVP use case but extensible for future features
    like batch processing, user associations, and advanced analytics.
    """
    
    __tablename__ = 'videos'
    
    # Primary key - auto-incrementing integer
    id = db.Column(db.Integer, primary_key=True)
    
    # YouTube video ID extracted from URL (e.g., "dQw4w9WgXcQ")
    # Max length 20 chars covers current YouTube ID format with room for growth
    # Note: Uniqueness is enforced by composite constraint with mode (see below)
    video_id = db.Column(db.String(20), nullable=False)

    # Summarization mode: "quick" or "indepth"
    # Allows storing multiple summaries for the same video (one per mode)
    # Default to "quick" for backward compatibility with existing records
    mode = db.Column(db.String(20), default='quick', nullable=False)
    
    # Video title extracted from YouTube metadata
    # 500 chars accommodates most YouTube titles with room for long titles
    title = db.Column(db.String(500), nullable=False)
    
    # Original URL submitted by user (for reference and debugging)
    # Supports various YouTube URL formats (youtube.com, youtu.be, etc.)
    url = db.Column(db.String(200), nullable=False)
    
    # Raw transcript text extracted from YouTube captions
    # TEXT type supports large transcripts (up to 65,535 chars in MySQL)
    # For longer content, could upgrade to LONGTEXT in production
    transcript = db.Column(db.Text)

    # AI-generated summary using LangChain + OpenAI
    # Changed from Text to JSON to support structured summaries with:
    # - quick_takeaway: Single sentence core message
    # - key_points: List of critical insights
    # - topics: Main themes with navigation
    # - timestamps: Key moments
    # - full_summary: Detailed narrative paragraphs
    # Backward compatible: handles both old text and new JSON formats
    summary = db.Column(db.JSON)
    
    # Processing status for workflow management and error recovery
    # States: 'pending' -> 'processing' -> 'completed' or 'failed'
    # Enables retry logic and prevents duplicate processing
    status = db.Column(db.String(20), default='pending')
    
    # Audit timestamps for debugging and analytics
    # created_at: When video was first submitted
    # updated_at: Last modification (auto-updated on changes)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite unique constraint: same video can have multiple summaries (one per mode)
    # This allows independent caching for Quick and In-Depth modes
    __table_args__ = (
        db.UniqueConstraint('video_id', 'mode', name='uix_video_mode'),
    )
    
    def to_dict(self):
        """
        Serialize Video object to dictionary for JSON API responses.

        Converts SQLAlchemy model to plain Python dict that can be
        JSON-serialized for API responses. Handles datetime conversion
        to ISO format for frontend consumption.

        Returns:
            dict: JSON-serializable representation of video data
        """
        return {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'url': self.url,
            'transcript': self.transcript,
            'summary': self.summary,
            'status': self.status,
            'mode': self.mode,  # Include mode in API response
            # Convert datetime objects to ISO format strings for JSON compatibility
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

