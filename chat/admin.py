from django.contrib import admin
from .models import ChatSession, Message,SessionUser
# Register your models here.

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at' , 'closed_at' , 'is_open' ,'description' , 'created_by')
admin.site.register(ChatSession, ChatSessionAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'content', 'timestamp')
admin.site.register(Message, MessageAdmin)

class SessionUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'token')
admin.site.register(SessionUser, SessionUserAdmin)



