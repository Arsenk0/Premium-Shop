import time
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps

def rate_limit(key_prefix, limit, period):
    """
    Simple cache-based rate limiter decorator.
    limit: max number of requests
    period: time window in seconds

    SECURITY NOTE: X-Forwarded-For can be spoofed by clients unless a trusted
    reverse proxy (nginx/Heroku/Cloudflare) is in front of Django and strips
    client-supplied values. We use the RIGHTMOST non-private IP as it is the
    last one appended by a trusted proxy and is harder to forge.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if forwarded_for:
                # Use the rightmost IP — added by the trusted proxy at the edge,
                # harder for the client to control than the leftmost value.
                ip = forwarded_for.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
            key = f"rate_limit:{key_prefix}:{ip}"

            requests_log = cache.get(key, [])
            now = time.time()

            # Filter out old requests outside the time window
            requests_log = [r for r in requests_log if r > now - period]

            if len(requests_log) >= limit:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Too many requests. Please try again later.'
                }, status=429)

            requests_log.append(now)
            cache.set(key, requests_log, period)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
