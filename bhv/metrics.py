"""Monitoring and metrics for BHV application."""
import time
import logging
from typing import Dict, List
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and track application metrics."""
    
    def __init__(self):
        self.requests: List[Dict] = []
        self.errors: List[Dict] = []
        self.max_history = 1000
    
    def record_request(self, endpoint: str, method: str, duration: float, status: int):
        """Record HTTP request metrics."""
        self.requests.append({
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status': status,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only recent history
        if len(self.requests) > self.max_history:
            self.requests = self.requests[-self.max_history:]
    
    def record_error(self, endpoint: str, error: str, error_type: str):
        """Record error metrics."""
        self.errors.append({
            'endpoint': endpoint,
            'error': error,
            'error_type': error_type,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only recent history
        if len(self.errors) > self.max_history:
            self.errors = self.errors[-self.max_history:]
    
    def get_stats(self, minutes: int = 5) -> Dict:
        """Get metrics for last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent_requests = [r for r in self.requests if r['timestamp'] > cutoff]
        recent_errors = [e for e in self.errors if e['timestamp'] > cutoff]
        
        total_requests = len(recent_requests)
        total_errors = len(recent_errors)
        
        if total_requests == 0:
            return {
                'total_requests': 0,
                'total_errors': 0,
                'error_rate': 0,
                'avg_response_time': 0,
                'slowest_endpoint': None
            }
        
        # Calculate averages
        avg_duration = sum(r['duration'] for r in recent_requests) / total_requests
        
        # Find slowest endpoint
        slowest = max(recent_requests, key=lambda r: r['duration']) if recent_requests else None
        
        return {
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0,
            'avg_response_time': avg_duration,
            'slowest_endpoint': f"{slowest['method']} {slowest['endpoint']}" if slowest else None,
            'slowest_duration': slowest['duration'] if slowest else 0
        }
    
    def clear(self):
        """Clear all metrics."""
        self.requests = []
        self.errors = []


metrics = MetricsCollector()


def track_metrics(func):
    """Decorator to track endpoint metrics."""
    @wraps(func)
    async def async_wrapper(*args, request=None, **kwargs):
        start = time.time()
        try:
            result = await func(*args, request=request, **kwargs)
            duration = time.time() - start
            if request:
                metrics.record_request(
                    request.url.path,
                    request.method,
                    duration,
                    200
                )
            return result
        except Exception as e:
            duration = time.time() - start
            if request:
                metrics.record_request(
                    request.url.path,
                    request.method,
                    duration,
                    500
                )
                metrics.record_error(
                    request.url.path,
                    str(e),
                    type(e).__name__
                )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, request=None, **kwargs):
        start = time.time()
        try:
            result = func(*args, request=request, **kwargs)
            duration = time.time() - start
            if request:
                metrics.record_request(
                    request.url.path,
                    request.method,
                    duration,
                    200
                )
            return result
        except Exception as e:
            duration = time.time() - start
            if request:
                metrics.record_request(
                    request.url.path,
                    request.method,
                    duration,
                    500
                )
                metrics.record_error(
                    request.url.path,
                    str(e),
                    type(e).__name__
                )
            raise
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
