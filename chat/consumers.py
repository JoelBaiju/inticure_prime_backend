
import json
import bleach
from datetime import datetime, timezone, timedelta
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import SessionUser, Message

class SecureSupportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Secure WebSocket connection with token validation
        """
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        
        # Get token from query string
        query_string = parse_qs(self.scope.get('query_string', b'').decode())
        self.token = query_string.get('token', [None])[0]
        
        if not self.token:
            await self.close(code=4001)  # Custom close code for missing token
            return

        # Verify session and token
        self.user, self.session_user = await self.verify_session_access(self.session_id, self.token)
        
        if not self.user or not self.session_user:
            await self.close(code=4003)  # Custom close code for invalid token
            return

        # Check if session is expired
        if await self.is_session_expired():
            await self.close(code=4004)  # Custom close code for expired session
            return

        # Add to channel group
        self.session_group_name = f'session_{self.session_id}'
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def verify_session_access(self, session_id, token):
        """
        Verify session access with token validation
        """
        try:
            # Convert session_id to integer
            session_id_int = int(session_id)
            session_user = SessionUser.objects.select_related('user', 'session').get(
                session_id=session_id_int,
                token=token,
                is_active=True
            )
            return session_user.user, session_user
        except (SessionUser.DoesNotExist, ValueError):
            return None, None

    @database_sync_to_async
    def is_session_expired(self):
        """
        Check if session or token is expired
        """
        return self.session_user.expires_at < datetime.now(timezone.utc)

    @database_sync_to_async
    def get_chat_history(self):
        """
        Load previous messages for the session
        """
        try:
            messages = self.session_user.session.messages.select_related('sender').order_by('timestamp')
            
            chat_history = []
            for message in messages:
                # Get sender display name
                sender_display_name = self.get_sender_display_name(message.sender)
                
                chat_history.append({
                    'id': message.id,
                    'content': message.content,
                    'sender_id': str(message.sender.id),
                    'sender_name': sender_display_name,
                    'timestamp': message.timestamp.isoformat(),
                    'isCurrentUser': message.sender.id == self.user.id
                })
                if message.sender != self.user:
                    message.is_read =True
                    message.save()
            
            return chat_history
        except Exception as e:
            print(f"Error loading chat history: {e}")
            return []

    def get_sender_display_name(self, sender):
        """
        Get appropriate display name for sender based on their role
        """
        try:
            # Check if admin/superuser
            if sender.is_superuser:
                return "Inticure Support"
            
            # Check if doctor
            if hasattr(sender, 'doctorprofiles') and sender.doctorprofiles.exists():
                doctor_profile = sender.doctorprofiles.first()
                return doctor_profile.first_name if doctor_profile.first_name else sender.username
            
            # Check if customer
            if hasattr(sender, 'customerprofile'):
                return sender.first_name if sender.first_name else sender.username
            
            # Fallback to user's full name or username
            return sender.get_full_name() or sender.username
        except Exception:
            return sender.username

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message with content sanitization
        """
        # Sanitize HTML content
        clean_content = bleach.clean(
            content,
            tags=['b', 'i', 'u', 'em', 'strong', 'a'],
            attributes={'a': ['href', 'title']},
            strip=True
        )

        # Validate content length
        if len(clean_content) > 2000:
            raise ValueError("Message too long")

        # Validate content is not empty after sanitization
        if not clean_content.strip():
            raise ValueError("Message cannot be empty")

        message = Message.objects.create(
            session=self.session_user.session,
            sender=self.user,
            content=clean_content
        )
        return message

    async def receive(self, text_data):
        """
        Secure message handling
        """
        try:
            data = json.loads(text_data)
            event_type = data.get('type')

            if event_type == 'load_history':
                # Send chat history to the client
                chat_history = await self.get_chat_history()
                await self.send(text_data=json.dumps({
                    'type': 'chat_history',
                    'messages': chat_history
                }))

            elif event_type == 'message':
                content = data.get('message', '')
                
                # Basic rate limiting
                if await self.is_flooding():
                    await self.close(code=4005)  # Custom close code for flooding
                    return

                # Check if session is still open
                if not await self.is_session_open():
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'This chat session is closed.'
                    }))
                    return

                saved_message = await self.save_message(content)
                sender_display_name = self.get_sender_display_name(saved_message.sender)

                # Send to all users in the group
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': str(saved_message.id),
                        'sender_id': str(saved_message.sender.id),
                        'sender_name': sender_display_name,
                        'content': saved_message.content,
                        'timestamp': saved_message.timestamp.isoformat(),
                    }
                )

            elif event_type == 'typing':
                sender_display_name = self.get_sender_display_name(self.user)
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'typing_event',
                        'user_id': str(self.user.id),
                        'sender_name': sender_display_name,
                        'is_typing': bool(data.get('is_typing', False)),
                    }
                )

        except json.JSONDecodeError:
            await self.close(code=4002)  # Invalid JSON
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        except Exception as e:
            print(f"Unexpected error in WebSocket receive: {e}")
            await self.close(code=4000)  # Generic error

    @database_sync_to_async
    def is_session_open(self):
        """
        Check if the session is still open for new messages
        """
        try:
            # Refresh session data
            self.session_user.session.refresh_from_db()
            return self.session_user.session.is_open
        except Exception:
            return False

    @database_sync_to_async
    def is_flooding(self):
        """
        Basic flood protection - check for too many messages in short time
        """
        try:
            recent_messages = Message.objects.filter(
                sender=self.user,
                session=self.session_user.session,
                timestamp__gte=datetime.now(timezone.utc) - timedelta(seconds=10)
            ).count()
            return recent_messages > 5
        except Exception:
            return False

    async def chat_message(self, event):
        """
        Send message to WebSocket - FIXED to include isCurrentUser
        """
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'isCurrentUser': event['sender_id'] == str(self.user.id)  # Calculate for each user
        }))

    async def typing_event(self, event):
        """
        Send typing indicator to WebSocket
        """
        if event['user_id'] != str(self.user.id):  # Don't send own typing indicators
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'sender_name': event['sender_name'],
                'is_typing': event['is_typing'],
            }))

    async def disconnect(self, close_code):
        """
        Clean up on disconnect
        """
        if hasattr(self, 'session_group_name'):
            await self.channel_layer.group_discard(
                self.session_group_name,
                self.channel_name
            )





