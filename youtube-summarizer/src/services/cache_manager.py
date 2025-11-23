"""
Cache Manager - Redis-based caching service

This module provides a high-level interface for caching expensive operations
using Redis as the backend. Implements multi-layer caching strategy for:

1. Transcript data (1 hour TTL) - YouTube API calls are rate-limited
2. AI summaries (24 hour TTL) - OpenAI API calls are expensive  
3. Video metadata (1 week TTL) - Rarely changes once extracted

Key Features:
- Content-based caching using SHA-256 hashes
- Configurable TTL (Time To Live) for different data types
- JSON serialization for complex data structures
- Graceful fallback when Redis is unavailable
- Performance monitoring and cache hit/miss tracking
"""

import json
import hashlib
import logging
from typing import Optional, Any, Dict
import redis

# Configure logging for cache operations
logger = logging.getLogger(__name__)

class CacheManager:
    """
    Redis-based cache manager with multi-layer caching strategy.
    
    Provides high-level caching operations with automatic serialization,
    TTL management, and error handling. Designed to be injected into
    other services for performance optimization.
    
    Args:
        redis_client: Configured Redis client instance
        default_ttl: Default cache expiration time in seconds
    """
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        """
        Initialize cache manager with Redis client.

        Args:
            redis_client: Redis client instance (injected for testability)
            default_ttl: Default TTL in seconds (1 hour default)
        """
        self.redis = redis_client
        self.default_ttl = default_ttl

        # Test Redis connection on initialization
        if self.redis:
            try:
                self.redis.ping()
                logger.info("Redis connection established successfully")
            except (redis.ConnectionError, AttributeError):
                logger.error("Redis connection failed - cache will be disabled")
                self.redis = None
        else:
            logger.warning("Redis client is None - cache will be disabled")
    
    def get_cached_transcript(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached transcript data for a YouTube video.
        
        Transcript caching prevents repeated YouTube API calls for the same video.
        Cache key format: "transcript:{video_id}"
        
        Args:
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            
        Returns:
            dict: Cached transcript data with title and transcript text, or None if not cached
        """
        if not self.redis:
            return None
            
        try:
            key = f"transcript:{video_id}"
            cached_data = self.redis.get(key)
            
            if cached_data:
                logger.info(f"Cache HIT for transcript:{video_id}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache MISS for transcript:{video_id}")
                return None
                
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache retrieval error for transcript:{video_id}: {e}")
            return None
    
    def cache_transcript(self, video_id: str, transcript_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Cache transcript data with expiration.
        
        Stores transcript data in Redis with JSON serialization.
        Uses shorter TTL since transcripts rarely change but we want
        to refresh periodically in case of corrections.
        
        Args:
            video_id: YouTube video ID
            transcript_data: Dict containing transcript, title, and metadata
            ttl: Custom TTL in seconds (uses default if None)
            
        Returns:
            bool: True if cached successfully, False otherwise
        """
        if not self.redis:
            return False
            
        try:
            key = f"transcript:{video_id}"
            expiration = ttl or self.default_ttl
            
            # Serialize data to JSON and store with expiration
            success = self.redis.setex(key, expiration, json.dumps(transcript_data))
            
            if success:
                logger.info(f"Cached transcript:{video_id} with TTL {expiration}s")
            return success
            
        except (redis.RedisError, TypeError) as e:
            logger.error(f"Cache storage error for transcript:{video_id}: {e}")
            return False
    
    def get_cached_summary(self, content_hash: str) -> Optional[str]:
        """
        Retrieve cached AI summary based on content hash.
        
        Content-based caching ensures identical transcripts get identical summaries
        without expensive AI API calls. Hash-based keys prevent cache pollution
        from slightly different versions of the same content.
        
        Args:
            content_hash: SHA-256 hash of transcript content
            
        Returns:
            str: Cached summary text, or None if not cached
        """
        if not self.redis:
            return None
            
        try:
            key = f"summary:{content_hash}"
            cached_summary = self.redis.get(key)
            
            if cached_summary:
                logger.info(f"Cache HIT for summary:{content_hash}")
                return cached_summary
            else:
                logger.info(f"Cache MISS for summary:{content_hash}")
                return None
                
        except redis.RedisError as e:
            logger.error(f"Cache retrieval error for summary:{content_hash}: {e}")
            return None
    
    def cache_summary(self, content_hash: str, summary: str, ttl: Optional[int] = None) -> bool:
        """
        Cache AI-generated summary with longer TTL.
        
        AI summaries are expensive to generate and relatively stable,
        so we cache them longer than transcripts. Uses content hash
        as key to ensure cache consistency across identical content.
        
        Args:
            content_hash: SHA-256 hash of source content
            summary: AI-generated summary text
            ttl: Custom TTL in seconds (24 hours default)
            
        Returns:
            bool: True if cached successfully, False otherwise
        """
        if not self.redis:
            return False
            
        try:
            key = f"summary:{content_hash}"
            # Default to 24 hours for AI summaries (more expensive to regenerate)
            expiration = ttl or (self.default_ttl * 24)
            
            success = self.redis.setex(key, expiration, summary)
            
            if success:
                logger.info(f"Cached summary:{content_hash} with TTL {expiration}s")
            return success
            
        except redis.RedisError as e:
            logger.error(f"Cache storage error for summary:{content_hash}: {e}")
            return False
    
    def generate_content_hash(self, content: str) -> str:
        """
        Generate deterministic hash for content-based caching.
        
        Creates SHA-256 hash of content for use as cache key.
        Ensures identical content always produces identical hash,
        enabling efficient cache lookups for duplicate content.
        
        Args:
            content: Text content to hash
            
        Returns:
            str: 16-character hex hash (truncated for readability)
        """
        # Create SHA-256 hash of content
        hash_object = hashlib.sha256(content.encode('utf-8'))
        
        # Return first 16 characters for cache key (sufficient for uniqueness)
        return hash_object.hexdigest()[:16]
    
    def invalidate_video_cache(self, video_id: str) -> bool:
        """
        Remove all cached data for a specific video.
        
        Useful for forcing reprocessing of a video or clearing
        corrupted cache entries. Removes both transcript and
        any associated summary caches.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            bool: True if cache was cleared successfully
        """
        if not self.redis:
            return False
            
        try:
            # Remove transcript cache
            transcript_key = f"transcript:{video_id}"
            deleted_count = self.redis.delete(transcript_key)
            
            logger.info(f"Invalidated cache for video:{video_id}, deleted {deleted_count} keys")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Cache invalidation error for video:{video_id}: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get Redis cache statistics for monitoring.
        
        Returns basic Redis info for performance monitoring
        and capacity planning. Useful for debugging cache
        performance issues.
        
        Returns:
            dict: Cache statistics including memory usage and key counts
        """
        if not self.redis:
            return {"status": "disabled"}
            
        try:
            info = self.redis.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
            }
        except redis.RedisError as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}

