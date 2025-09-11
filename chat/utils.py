from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from datetime import timedelta

def rate_limit(rate):
    """
    Decorator for rate limiting views
    Usage: @rate_limit(rate='5/m')
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Create a unique key for the user
            key = f'rl:{request.user.id}:{request.path}'
            
            # Get current count
            current = cache.get(key, 0)
            
            # Check rate limit
            if current >= int(rate.split('/')[0]):
                raise PermissionDenied("Rate limit exceeded")
                
            # Increment count
            cache.set(key, current + 1, timeout=60)  # 1 minute window
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator