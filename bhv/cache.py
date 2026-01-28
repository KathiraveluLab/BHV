"""Caching layer for BHV application."""
import os
import json
from typing import Optional, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# In-memory cache as fallback
_memory_cache = {}

class CacheManager:
    """Manages caching with Redis fallback to memory."""
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = os.environ.get('REDIS_URL') is not None
        if self.use_redis:
            try:
                import redis
                self.redis_client = redis.from_url(os.environ.get('REDIS_URL'))
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}. Using memory cache.")
                self.use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.use_redis and self.redis_client:
                val = self.redis_client.get(key)
                return json.loads(val) if val else None
            else:
                return _memory_cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                _memory_cache[key] = value
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                _memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            else:
                matches = [k for k in _memory_cache if pattern.replace('*', '') in k]
                for k in matches:
                    _memory_cache.pop(k, None)
                return len(matches)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error: {e}")
            return 0


cache = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function args."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)
