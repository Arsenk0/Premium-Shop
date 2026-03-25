import time
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps

def rate_limit(key_prefix, limit, period):
    """
    Simple cache-based rate limiter decorator.
    limit: max number of requests
    period: time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Use X-Forwarded-For if behind proxy, fall back to REMOTE_ADDR
            forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            ip = forwarded_for.split(',')[0].strip() if forwarded_for else request.META.get('REMOTE_ADDR')
            key = f"rate_limit:{key_prefix}:{ip}"
            
            requests = cache.get(key, [])
            now = time.time()
            
            # Filter out old requests
            requests = [r for r in requests if r > now - period]
            
            if len(requests) >= limit:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Too many requests. Please try again later.'
                }, status=429)
            
            requests.append(now)
            cache.set(key, requests, period)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
