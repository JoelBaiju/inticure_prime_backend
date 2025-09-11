from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True)
    is_open = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100, null=True)  # could later be FK if linked to a user
    expires_at = models.DateTimeField(null=True, blank=True)


class SessionUser(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        null=True,
        related_name='session_users'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # ✅ safe lazy reference to custom user
        on_delete=models.CASCADE,
        null=True
    )
    token = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)


class Message(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        null=True,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # ✅ safe reference
        on_delete=models.CASCADE,
        null=True
    )
    content = models.TextField(null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']
