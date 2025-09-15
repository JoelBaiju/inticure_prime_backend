from celery import shared_task
from django.utils import timezone
from .models import ChatSession


@shared_task
def close_expired_chat_sessions():
    now = timezone.now()
    expired_sessions = ChatSession.objects.filter(expires_at__lt=now)
    count = expired_sessions.count()
    expired_sessions.update(is_open=False)
    print( f"Closed {count} expired chat sessions.")
    return f"Closed {count} expired chat sessions."