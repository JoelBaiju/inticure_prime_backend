from celery import shared_task
from django.utils import timezone
from .models import ChatSession



@shared_task
def close_expired_chat_sessions():
    now = timezone.now()
    BATCH_SIZE = 1000
    
    while True:
        ids = list(
            ChatSession.objects
            .filter(expires_at__lt=now, is_open=True)
            .values_list("id", flat=True)[:BATCH_SIZE]
        )
        
        if not ids:
            break
        
        ChatSession.objects.filter(id__in=ids).update(is_open=False)
    
    print("Closed expired chat sessions.")
    return "Closed expired chat sessions."
