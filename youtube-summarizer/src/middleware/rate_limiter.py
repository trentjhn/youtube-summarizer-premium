"""
Rate Limiter - Request rate limiting middleware

Implements rate limiting to prevent abuse and ensure fair resource usage.
Uses Flask-Limiter for flexible rate limiting configuration.
"""

import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify

logger = logging.getLogger(__name__)


def create_limiter():
    """
    Create and configure a rate limiter instance.
    
    Returns:
        Limiter: Configured Flask-Limiter instance
    """
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",  # Use in-memory storage for MVP
        # For production, use Redis: storage_uri="redis://localhost:6379"
    )
    
    return limiter


def init_rate_limiting(app, limiter):
    """
    Initialize rate limiting for the Flask app.
    
    Args:
        app: Flask application instance
        limiter: Limiter instance
    """
    limiter.init_app(app)
    
    # Register error handler for rate limit exceeded
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors."""
        logger.warning(f"Rate limit exceeded: {e.description}")
        return jsonify({
            'error': 'Too many requests. Please try again later.',
            'error_type': 'rate_limit',
            'retry_after': e.get_headers()[0][1] if e.get_headers() else None
        }), 429
    
    logger.info("Rate limiting initialized")


# Rate limit decorators for specific endpoints
def limit_video_processing():
    """
    Rate limit decorator for video processing endpoint.
    
    Limits to 10 requests per minute per IP address.
    This prevents abuse while allowing legitimate usage.
    """
    return "10 per minute"


def limit_general_api():
    """
    Rate limit decorator for general API endpoints.
    
    Limits to 30 requests per minute per IP address.
    """
    return "30 per minute"

