"""
Error Handler - Centralized error handling and user-friendly error messages

This module provides utilities for handling errors gracefully and returning
user-friendly error messages. Implements retry logic and error categorization.
"""

import logging
import time
from typing import Callable, Any, Optional, Type
from functools import wraps
from flask import jsonify

logger = logging.getLogger(__name__)


class VideoProcessingError(Exception):
    """Base exception for video processing errors."""
    pass


class TranscriptExtractionError(VideoProcessingError):
    """Raised when transcript extraction fails."""
    pass


class AIProcessingError(VideoProcessingError):
    """Raised when AI summarization fails."""
    pass


class InvalidURLError(VideoProcessingError):
    """Raised when YouTube URL is invalid."""
    pass


class RateLimitError(VideoProcessingError):
    """Raised when API rate limit is exceeded."""
    pass


def get_user_friendly_error(error: Exception) -> str:
    """
    Convert technical errors to user-friendly messages.
    
    Args:
        error: The exception that occurred
        
    Returns:
        str: User-friendly error message
    """
    error_str = str(error).lower()
    
    # Transcript extraction errors
    if "no transcripts available" in error_str:
        return "This video doesn't have available transcripts. Try another video."
    
    if "invalid youtube url" in error_str or "could not extract video id" in error_str:
        return "Please enter a valid YouTube URL (e.g., https://youtube.com/watch?v=...)"
    
    if "transcript extraction" in error_str:
        return "Failed to extract transcript. The video may not have captions available."
    
    # AI processing errors
    if "openai" in error_str or "api" in error_str:
        return "AI processing temporarily unavailable. Please try again in a moment."
    
    if "rate limit" in error_str or "quota" in error_str:
        return "Service is busy. Please wait a moment and try again."
    
    if "timeout" in error_str:
        return "Request took too long. Please try again."
    
    # Network errors
    if "connection" in error_str or "network" in error_str:
        return "Network error. Please check your connection and try again."
    
    # Default message
    return "An error occurred while processing the video. Please try again."


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated function that retries on failure
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def handle_api_error(func: Callable) -> Callable:
    """
    Decorator for handling API errors and returning proper HTTP responses.

    Catches VideoProcessingError and its subclasses and converts them
    to appropriate HTTP error responses.

    Args:
        func: Flask route handler function

    Returns:
        Decorated function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidURLError as e:
            logger.warning(f"Invalid URL error: {e}")
            return jsonify({
                'error': get_user_friendly_error(e),
                'error_type': 'invalid_url'
            }), 400
        except TranscriptExtractionError as e:
            logger.warning(f"Transcript extraction error: {e}")
            return jsonify({
                'error': get_user_friendly_error(e),
                'error_type': 'transcript_extraction'
            }), 500
        except RateLimitError as e:
            logger.warning(f"Rate limit error: {e}")
            return jsonify({
                'error': get_user_friendly_error(e),
                'error_type': 'rate_limit'
            }), 429
        except AIProcessingError as e:
            logger.warning(f"AI processing error: {e}")
            return jsonify({
                'error': get_user_friendly_error(e),
                'error_type': 'ai_processing'
            }), 500
        except VideoProcessingError as e:
            logger.error(f"Video processing error: {e}")
            return jsonify({
                'error': get_user_friendly_error(e),
                'error_type': 'processing'
            }), 500
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return jsonify({
                'error': 'An unexpected error occurred. Please try again.',
                'error_type': 'unknown'
            }), 500

    return wrapper

