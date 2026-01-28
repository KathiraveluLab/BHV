"""Rate limiting for BHV application."""
import time
from typing import Dict, Tuple
from functools import wraps
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter using in-memory tracking."""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, limit: int = 30, window: int = 60) -> bool:
        """Check if request is allowed within rate limit."""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(now)
        return True
    
    def cleanup_old_entries(self, window: int = 3600):
        """Remove entries older than window to prevent memory leak."""
        now = time.time()
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window
            ]
            if not self.requests[key]:
                del self.requests[key]


rate_limiter = RateLimiter()


def rate_limit(limit: int = 30, window: int = 60):
    """Decorator to rate limit endpoints."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, request=None, **kwargs):
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = request.client.host if request.client else "unknown"
            key = f"{func.__name__}:{client_ip}"
            
            if not rate_limiter.is_allowed(key, limit, window):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            return await func(*args, request=request, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, request=None, **kwargs):
            if not request:
                return func(*args, **kwargs)
            
            client_ip = request.client.host if request.client else "unknown"
            key = f"{func.__name__}:{client_ip}"
            
            if not rate_limiter.is_allowed(key, limit, window):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            return func(*args, request=request, **kwargs)
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
