"""
Middleware package for YouTube Summarizer

Contains middleware for rate limiting, error handling, and other cross-cutting concerns.
"""

from .rate_limiter import (
    create_limiter,
    init_rate_limiting,
    limit_video_processing,
    limit_general_api
)

__all__ = [
    'create_limiter',
    'init_rate_limiting',
    'limit_video_processing',
    'limit_general_api'
]

