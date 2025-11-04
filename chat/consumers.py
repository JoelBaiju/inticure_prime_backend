
# import json
# import bleach
# from datetime import datetime, timezone, timedelta
# from urllib.parse import parse_qs
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import User
# from .models import SessionUser, Message


# import logging
# logger = logging.getLogger(__name__)

# class SecureSupportConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         """
#         Secure WebSocket connection with token validation
#         """
#         self.session_id = self.scope['url_route']['kwargs']['session_id']
        
#         # Get token from query string
#         query_string = parse_qs(self.scope.get('query_string', b'').decode())
#         self.token = query_string.get('token', [None])[0]
        
#         if not self.token:
#             await self.close(code=4001)  # Custom close code for missing token
#             return

#         # Verify session and token
#         self.user, self.session_user = await self.verify_session_access(self.session_id, self.token)
        
#         if not self.user or not self.session_user:
#             await self.close(code=4003)  # Custom close code for invalid token
#             return

#         # Check if session is expired
#         if await self.is_session_expired():
#             await self.close(code=4004)  # Custom close code for expired session
#             return

#         # Add to channel group
#         self.session_group_name = f'session_{self.session_id}'
#         await self.channel_layer.group_add(
#             self.session_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     @database_sync_to_async
#     def verify_session_access(self, session_id, token):
#         """
#         Verify session access with token validation
#         """
#         try:
#             # Convert session_id to integer
#             session_id_int = int(session_id)
#             session_user = SessionUser.objects.select_related('user', 'session').get(
#                 session_id=session_id_int,
#                 token=token,
#                 is_active=True
#             )
#             return session_user.user, session_user
#         except (SessionUser.DoesNotExist, ValueError):
#             return None, None

#     @database_sync_to_async
#     def is_session_expired(self):
#         """
#         Check if session or token is expired
#         """
#         return self.session_user.expires_at < datetime.now(timezone.utc)

#     @database_sync_to_async
#     def get_chat_history(self):
#         """
#         Load previous messages for the session
#         """
#         try:
#             messages = self.session_user.session.messages.select_related('sender').order_by('timestamp')
            
#             chat_history = []
#             for message in messages:
#                 # Get sender display name
#                 sender_display_name = self.get_sender_display_name(message.sender)
                
#                 chat_history.append({
#                     'id': message.id,
#                     'content': message.content,
#                     'sender_id': str(message.sender.id),
#                     'sender_name': sender_display_name,
#                     'timestamp': message.timestamp.isoformat(),
#                     'isCurrentUser': message.sender.id == self.user.id
#                 })
#                 if message.sender != self.user:
#                     message.is_read =True
#                     message.save()
            
#             return chat_history
#         except Exception as e:
#             print(f"Error loading chat history: {e}")
#             return []

#     def get_sender_display_name(self, sender):
#         """
#         Get appropriate display name for sender based on their role
#         """
#         try:
#             # Check if admin/superuser
#             if sender.is_superuser:
#                 return "Inticure Support"
            
#             # Check if doctor
#             if hasattr(sender, 'doctorprofiles') and sender.doctorprofiles.exists():
#                 doctor_profile = sender.doctorprofiles.first()
#                 return doctor_profile.first_name if doctor_profile.first_name else sender.username
            
#             # Check if customer
#             if hasattr(sender, 'customerprofile'):
#                 return sender.first_name if sender.first_name else sender.username
            
#             # Fallback to user's full name or username
#             return sender.get_full_name() or sender.username
#         except Exception:
#             return sender.username

#     @database_sync_to_async
#     def save_message(self, content):
#         """
#         Save message with content sanitization
#         """
#         # Sanitize HTML content
#         clean_content = bleach.clean(
#             content,
#             tags=['b', 'i', 'u', 'em', 'strong', 'a'],
#             attributes={'a': ['href', 'title']},
#             strip=True
#         )

#         # Validate content length
#         if len(clean_content) > 2000:
#             raise ValueError("Message too long")

#         # Validate content is not empty after sanitization
#         if not clean_content.strip():
#             raise ValueError("Message cannot be empty")

#         message = Message.objects.create(
#             session=self.session_user.session,
#             sender=self.user,
#             content=clean_content
#         )
#         return message

#     async def receive(self, text_data):
#         """
#         Secure message handling
#         """
#         try:
#             data = json.loads(text_data)
#             event_type = data.get('type')

#             if event_type == 'load_history':
#                 # Send chat history to the client
#                 chat_history = await self.get_chat_history()
#                 await self.send(text_data=json.dumps({
#                     'type': 'chat_history',
#                     'messages': chat_history
#                 }))

#             elif event_type == 'message':
#                 content = data.get('message', '')
                
#                 # Basic rate limiting
#                 if await self.is_flooding():
#                     await self.close(code=4005)  # Custom close code for flooding
#                     return

#                 # Check if session is still open
#                 if not await self.is_session_open():
#                     await self.send(text_data=json.dumps({
#                         'type': 'error',
#                         'message': 'This chat session is closed.'
#                     }))
#                     return

#                 saved_message = await self.save_message(content)
#                 sender_display_name = self.get_sender_display_name(saved_message.sender)

#                 # Send to all users in the group
#                 await self.channel_layer.group_send(
#                     self.session_group_name,
#                     {
#                         'type': 'chat_message',
#                         'message_id': str(saved_message.id),
#                         'sender_id': str(saved_message.sender.id),
#                         'sender_name': sender_display_name,
#                         'content': saved_message.content,
#                         'timestamp': saved_message.timestamp.isoformat(),
#                     }
#                 )

#             elif event_type == 'typing':
#                 sender_display_name = self.get_sender_display_name(self.user)
#                 await self.channel_layer.group_send(
#                     self.session_group_name,
#                     {
#                         'type': 'typing_event',
#                         'user_id': str(self.user.id),
#                         'sender_name': sender_display_name,
#                         'is_typing': bool(data.get('is_typing', False)),
#                     }
#                 )

#         except json.JSONDecodeError:
#             await self.close(code=4002)  # Invalid JSON
#         except ValueError as e:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': str(e)
#             }))
#         except Exception as e:
#             print(f"Unexpected error in WebSocket receive: {e}")
#             await self.close(code=4000)  # Generic error

#     @database_sync_to_async
#     def is_session_open(self):
#         """
#         Check if the session is still open for new messages
#         """
#         try:
#             # Refresh session data
#             self.session_user.session.refresh_from_db()
#             return self.session_user.session.is_open
#         except Exception:
#             return False

#     @database_sync_to_async
#     def is_flooding(self):
#         """
#         Basic flood protection - check for too many messages in short time
#         """
#         try:
#             recent_messages = Message.objects.filter(
#                 sender=self.user,
#                 session=self.session_user.session,
#                 timestamp__gte=datetime.now(timezone.utc) - timedelta(seconds=10)
#             ).count()
#             return recent_messages > 5
#         except Exception:
#             return False

#     async def chat_message(self, event):
#         """
#         Send message to WebSocket - FIXED to include isCurrentUser
#         """
#         await self.send(text_data=json.dumps({
#             'type': 'message',
#             'message_id': event['message_id'],
#             'sender_id': event['sender_id'],
#             'sender_name': event['sender_name'],
#             'content': event['content'],
#             'timestamp': event['timestamp'],
#             'isCurrentUser': event['sender_id'] == str(self.user.id)  # Calculate for each user
#         }))

#     async def typing_event(self, event):
#         """
#         Send typing indicator to WebSocket
#         """
#         if event['user_id'] != str(self.user.id):  # Don't send own typing indicators
#             await self.send(text_data=json.dumps({
#                 'type': 'typing',
#                 'user_id': event['user_id'],
#                 'sender_name': event['sender_name'],
#                 'is_typing': event['is_typing'],
#             }))

#     async def disconnect(self, close_code):
#         """
#         Clean up on disconnect
#         """
#         if hasattr(self, 'session_group_name'):
#             await self.channel_layer.group_discard(
#                 self.session_group_name,
#                 self.channel_name
#             )





import json
import bleach
import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import SessionUser, Message
from general.notification_controller import send_wa_patient_chat_notification_to_specialist

logger = logging.getLogger(__name__)


class SecureSupportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Secure WebSocket connection with token validation
        """
        logger.debug("WebSocket connect() called.")

        try:
            self.session_id = self.scope['url_route']['kwargs'].get('session_id')
            logger.debug(f"Extracted session_id: {self.session_id}")

            # Get token from query string
            raw_qs = self.scope.get('query_string', b'').decode()
            query_string = parse_qs(raw_qs)
            logger.debug(f"Parsed query string: {query_string}")

            self.token = query_string.get('token', [None])[0]
            logger.debug(f"Extracted token: {self.token}")

            if not self.token:
                logger.warning("No token provided. Closing connection with code 4001.")
                await self.close(code=4001)
                return

            # Verify session and token
            logger.debug("Verifying session access...")
            self.user, self.session_user = await self.verify_session_access(self.session_id, self.token)
            logger.debug(f"verify_session_access() returned -> user: {self.user}, session_user: {self.session_user}")

            if not self.user or not self.session_user:
                logger.warning("Invalid session or token. Closing connection with code 4003.")
                await self.close(code=4003)
                return

            # Check if session is expired
            logger.debug("Checking if session is expired...")
            if await self.is_session_expired():
                logger.warning("Session is expired. Closing connection with code 4004.")
                await self.close(code=4004)
                return

            # Add to channel group
            self.session_group_name = f'session_{self.session_id}'
            logger.debug(f"Adding to channel group: {self.session_group_name}")
            await self.channel_layer.group_add(self.session_group_name, self.channel_name)

            logger.info("WebSocket connection accepted.")
            await self.accept()

        except Exception as e:
            logger.exception(f"Unexpected error in connect(): {e}")
            await self.close(code=4000)  # Generic error

    @database_sync_to_async
    def verify_session_access(self, session_id, token):
        """
        Verify session access with token validation and optional auto-renewal.
        """
        logger.debug(f"verify_session_access() called with session_id={session_id}, token={token}")
        try:
            session_id_int = int(session_id)
            logger.debug(f"Converted session_id to int: {session_id_int}")

            session_user = SessionUser.objects.select_related('user', 'session').get(
                session_id=session_id_int,
                token=token,
                is_active=True
            )
            logger.debug("SessionUser query successful.")

            # Auto-renew token if it's close to expiry or expired
            now = datetime.now(timezone.utc)
            if session_user.expires_at < now:
                logger.warning(f"SessionUser token expired at {session_user.expires_at}, renewing expiry.")
                session_user.expires_at = now + timedelta(hours=24)
                session_user.save(update_fields=["expires_at"])
                logger.info(f"Token renewed. New expiry: {session_user.expires_at}")

            return session_user.user, session_user

        except SessionUser.DoesNotExist:
            logger.warning("SessionUser.DoesNotExist - invalid session or token.")
            return None, None
        except ValueError as ve:
            logger.warning(f"ValueError converting session_id to int: {ve}")
            return None, None
        except Exception as e:
            logger.exception(f"Unexpected DB error in verify_session_access(): {e}")
            return None, None

    @database_sync_to_async
    def is_session_expired(self):
        """
        Check if session or token is expired
        """
        try:
            expired = self.session_user.expires_at < datetime.now(timezone.utc)
            logger.debug(f"Session expiration check: {expired}")
            return expired
        except Exception as e:
            logger.exception(f"Error in is_session_expired(): {e}")
            return True  # Fail safe

    @database_sync_to_async
    def get_chat_history(self):
        """
        Load previous messages for the session
        """
        logger.debug("Fetching chat history...")
        try:
            messages = self.session_user.session.messages.select_related('sender').order_by('timestamp')
            chat_history = []
            for message in messages:
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
                    message.is_read = True
                    message.save()
            logger.debug(f"Loaded {len(chat_history)} messages in chat history.")
            return chat_history
        except Exception as e:
            logger.exception(f"Error loading chat history: {e}")
            return []

    def get_sender_display_name(self, sender):
        """
        Get appropriate display name for sender based on their role
        """
        try:
            if sender.is_superuser:
                return "Inticure Support"
            if hasattr(sender, 'doctorprofiles') and sender.doctorprofiles.exists():
                doctor_profile = sender.doctorprofiles.first()
                return doctor_profile.first_name or sender.username
            if hasattr(sender, 'customerprofile'):
                return sender.first_name or sender.username
            return sender.get_full_name() or sender.username
        except Exception as e:
            logger.exception(f"Error getting sender display name: {e}")
            return sender.username

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message with content sanitization
        """
        logger.debug(f"save_message() called with content: {content}")
        try:
            clean_content = bleach.clean(
                content,
                tags=['b', 'i', 'u', 'em', 'strong', 'a'],
                attributes={'a': ['href', 'title']},
                strip=True
            )

            if len(clean_content) > 2000:
                logger.warning("Message too long after sanitization.")
                raise ValueError("Message too long")
            if not clean_content.strip():
                logger.warning("Message empty after sanitization.")
                raise ValueError("Message cannot be empty")

            message = Message.objects.create(
                session=self.session_user.session,
                sender=self.user,
                content=clean_content
            )
            session_users = self.session_user.session.session_users.all()
            doctor_user = None
            doctor_profile = None

            for su in session_users:
                # Check if this user has a linked doctor profile
                if hasattr(su.user, 'doctor_profile') and su.user.doctor_profile:
                    doctor_user = su.user
                    doctor_profile = su.user.doctor_profile
                    break

            if not self.user.is_staff and doctor_profile and doctor_profile.whatsapp_number:
                logger.debug(send_wa_patient_chat_notification_to_specialist(
                    f"{doctor_profile.whatsapp_country_code}{doctor_profile.whatsapp_number}",
                    f"{doctor_profile.salutation}. {doctor_profile.first_name}"
                ))

            logger.debug(f"Message saved successfully with id {message.id}")
            return message
        except Exception as e:
            logger.exception(f"Error saving message: {e}")
            raise

    async def receive(self, text_data):
        """
        Secure message handling
        """
        logger.debug(f"receive() called with raw data: {text_data}")
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            logger.debug(f"Parsed event type: {event_type}")

            if event_type == 'load_history':
                chat_history = await self.get_chat_history()
                await self.send(text_data=json.dumps({
                    'type': 'chat_history',
                    'messages': chat_history
                }))
                logger.debug("Sent chat history to client.")

            elif event_type == 'message':
                content = data.get('message', '')
                logger.debug(f"New message event with content: {content}")

                if await self.is_flooding():
                    logger.warning("Flooding detected. Closing with code 4005.")
                    await self.close(code=4005)
                    return

                if not await self.is_session_open():
                    logger.warning("Session is closed. Sending error to client.")
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'This chat session is closed.'
                    }))
                    return

                saved_message = await self.save_message(content)
                sender_display_name = self.get_sender_display_name(saved_message.sender)
                logger.debug(f"Broadcasting message {saved_message.id} to group {self.session_group_name}")

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
                logger.debug(f"Typing event by user {self.user.id}")
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
            logger.warning("Invalid JSON received. Closing with code 4002.")
            await self.close(code=4002)
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))
        except Exception as e:
            logger.exception(f"Unexpected error in receive(): {e}")
            await self.close(code=4000)

    @database_sync_to_async
    def is_session_open(self):
        """
        Check if the session is still open for new messages
        """
        try:
            self.session_user.session.refresh_from_db()
            is_open = self.session_user.session.is_open
            logger.debug(f"Session open check: {is_open}")
            return is_open
        except Exception as e:
            logger.exception(f"Error in is_session_open(): {e}")
            return False

    @database_sync_to_async
    def is_flooding(self):
        """
        Basic flood protection - check for too many messages in short time
        """
        try:
            count = Message.objects.filter(
                sender=self.user,
                session=self.session_user.session,
                timestamp__gte=datetime.now(timezone.utc) - timedelta(seconds=10)
            ).count()
            logger.debug(f"Flood check: {count} messages in last 10s")
            return count > 5
        except Exception as e:
            logger.exception(f"Error in is_flooding(): {e}")
            return False

    async def chat_message(self, event):
        logger.debug(f"Sending chat_message event to client: {event}")
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'isCurrentUser': event['sender_id'] == str(self.user.id)
        }))

    async def typing_event(self, event):
        if event['user_id'] != str(self.user.id):
            logger.debug(f"Sending typing_event to client: {event}")
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'sender_name': event['sender_name'],
                'is_typing': event['is_typing'],
            }))

    # async def disconnect(self, close_code):
    #     logger.info(f"WebSocket disconnected. Close code: {close_code}")
    #     try:
    #         if hasattr(self, 'session_group_name'):
    #             await self.channel_layer.group_discard(
    #                 self.session_group_name,
    #                 self.channel_name
    #             )
    #             logger.debug(f"Removed from group: {self.session_group_name}")
    #     except Exception as e:
    #         logger.exception(f"Error during disconnect: {e}")
    async def disconnect(self, close_code):
        logger.debug(f"WebSocket disconnected. Close code: {close_code}, channel_name: {self.channel_name}")
        if hasattr(self, "session_group_name"):
            logger.debug(f"Removing {self.channel_name} from group: {self.session_group_name}")
            await self.channel_layer.group_discard(self.session_group_name, self.channel_name)
        else:
            logger.debug("disconnect() called before group assignment!")
