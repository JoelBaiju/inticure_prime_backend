from celery import shared_task
from django.utils import timezone
from .models import ChatSession


@shared_task
def close_expired_chat_sessions():
    now = timezone.now()
    BATCH_SIZE = 1000
    while True:
        expired = ChatSession.objects.filter(expires_at__lt=now, is_open=True)[:BATCH_SIZE]
        if not expired: 
            break
        expired.update(is_open=False)


    print( f"Closed  expired chat sessions.")
    return f"Closed  expired chat sessions."