from django.core.exceptions import PermissionDenied
from .models import SessionUser
from datetime import datetime

def validate_session_token(view_func):
    """
    Decorator to validate session token
    """
    def wrapped_view(request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        token = request.GET.get('token') or request.COOKIES.get('chat_session_token')
        print(session_id,token)

        if not session_id or not token:
            raise PermissionDenied("Invalid session")
            
        try:
            session_user = SessionUser.objects.select_related('session', 'user').get(
                session_id=session_id,
                token=token,
                is_active=True,
                expires_at__gt=datetime.now()
            )
            
            # Verify user matches
            print(request.user , session_user.user)

            if session_user.user != request.user:
                raise PermissionDenied("User mismatch")
                
            # Check session is still open
            if not session_user.session.is_open:
                raise PermissionDenied("Session closed")
                
        except SessionUser.DoesNotExist:
            raise PermissionDenied("Invalid session token")
            
        return view_func(request, session_user=session_user, *args, **kwargs)
    return wrapped_view