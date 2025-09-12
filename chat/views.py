from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from chat.admin import SessionUserAdmin
from .models import ChatSession, SessionUser, Message
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession

User = get_user_model()

# @login_required
def create_session(request):
    if request.method == 'POST':
        complaint = request.POST.get('complaint')
        session = ChatSession.objects.create(
            patient=request.user,
            complaint=complaint
        )
        return redirect('session_detail', session_id=session.id)
    return render(request, 'create_session.html')

# @login_required
def assign_doctor(request, session_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    session = get_object_or_404(ChatSession, id=session_id)
    doctor_id = request.POST.get('doctor_id')
    doctor = get_object_or_404(User, id=doctor_id)
    
    session.doctor = doctor
    session.save()
    
    return JsonResponse({'success': True})

# @login_required
def close_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    
    # Only doctor or staff can close the session
    if request.user != session.doctor and not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    session.status = 'closed'
    session.closed_at = timezone.now()
    session.save()
    
    return JsonResponse({'success': True})

# @login_required
def session_detail(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    
    # Check if user is authorized to view this session
    if request.user != session.patient and request.user != session.doctor and not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    messages = session.messages.all().order_by('timestamp')
    
    return render(request, 'session_detail.html', {
        'session': session,
        'messages': messages,
    })


from analysis.models import *
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status




# # @permission_classes([IsAuthenticated])
# @api_view(['GET'])
# def initiate_chat_patient_doctor(request):
#     customre_user = User.objects.get(username = request.GET.get('username'))
#     appointment_id = request.GET.get('appointment_id')
    


#     appointment = get_object_or_404(AppointmentHeader, appointment_id = appointment_id)

#     if appointment.appointment_status not in ['confirmed','completed']:
#         return JsonResponse({'error': 'Appointment not confirmed'}, status=400)

#     chat_session = ChatSession.objects.create(
#         created_by = 'patient',
#         description = "Patient chat with doctor for appointment id: " + appointment_id,
#     )
#     session_user = SessionUser.objects.create(
#         session = chat_session,
#         user = customre_user,
#         token = uuid.uuid4(),
#     )
#     session_user_doctors = SessionUser.objects.create(
#         session = chat_session,
#         user = appointment.doctor.user,
#         token = uuid.uuid4(),
#     )

#     Message.objects.create(
#         session = chat_session,
#         sender = customre_user,
#         content = "Patient chat with doctor for appointment id: " + appointment_id,
#     )
  

#     return redirect(f'/chat/join/?session_id={chat_session.id}&token={session_user.token}')






# def join_chat(request):
#     session_id = request.GET.get('session_id')
#     token = request.GET.get('token')

#     session = get_object_or_404(ChatSession, id=session_id)
#     session_user = get_object_or_404(SessionUser, session=session, token=token)
#     if session_user.is_active == False:
#         return JsonResponse({'error': 'Session user not active'}, status=400)

#     session_user.is_active = True
#     session_user.save()
#     messages = session.messages.all().order_by('timestamp')
#     doctor=False
#     customer = False
#     if DoctorProfiles.objects.filter(user = session_user.user).exists():
#         doctor = DoctorProfiles.objects.get(user = session_user.user).first_name
#     elif CustomerProfile.objects.filter(user = session_user.user).exists():
#         customer = CustomerProfile.objects.get(user = session_user.user).user.first_name

    

#     return render(request, 'chat_box.html', {
#         'session': session,
#         'token': session_user.token,
#         'messages': messages,
#         'session_user': session_user,
#         "doctor":doctor if doctor else False,
#         "customer":customer if customer else False,


#     })


# def join_chat_doctor(request):
#     session_id = request.GET.get('session_id')
#     token = request.GET.get('token')
#     session = get_object_or_404(ChatSession, id=session_id)
#     session_user = get_object_or_404(SessionUser, session=session, token=token)
#     if session_user.is_active == False:
#         return JsonResponse({'error': 'Session user not active'}, status=400)
#     session_user.is_active = True
#     session_user.save()
#     messages = session.messages.all().order_by('timestamp')

    

import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import ChatSession, SessionUser, Message
from analysis.models import AppointmentHeader
from doctor.models import DoctorProfiles
from customer.models import CustomerProfile
from django.contrib.auth.models import User
from .utils import rate_limit
from .decorators import validate_session_token
from django.contrib.auth import login


@permission_classes([IsAuthenticated])
@api_view(['GET'])
@rate_limit(rate='5/m')
def initiate_chat_patient_doctor(request):
    """
    Secure version of chat initiation with:
    - Rate limiting
    - Proper authentication
    - Input validation
    - Session validation
    """
    try:
        # customer_user = request.user
        customer_user = User.objects.get(username = request.GET.get('username'))
        appointment_id = request.GET.get('appointment_id')
        
        if not appointment_id:
            return JsonResponse({'error': 'Appointment ID is required'}, status=400)

        appointment = get_object_or_404(AppointmentHeader, appointment_id=appointment_id)

        if appointment.appointment_status not in ['confirmed', 'completed']:
            return JsonResponse({'error': 'Appointment not confirmed'}, status=400)

        # Verify customer is part of this appointment
        if appointment.customer.user != customer_user:
            return JsonResponse({'error': 'Not authorized for this appointment'}, status=403)

        chat_session = ChatSession.objects.create(
            created_by='patient',
            description=f"Patient chat with doctor for appointment id: {appointment_id}",
            expires_at=timezone.now() + timedelta(hours=24)  # Session expires in 7 days

        )
        # Create session users with limited-time tokens
        session_user = SessionUser.objects.create(
            session=chat_session,
            user=customer_user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        session_user_doctor = SessionUser.objects.create(
            session=chat_session,
            user=appointment.doctor.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24))

        # Create initial message
        Message.objects.create(
            session=chat_session,
            sender=customer_user,
            content=f"Patient chat with doctor for appointment id: {appointment_id}")

        login(request, customer_user)

        # Use HTTPS and POST-redirect-GET pattern
        return redirect(f'/chat/join/?session_id={chat_session.id}&token={session_user.token}')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@permission_classes([IsAuthenticated])
@api_view(['GET'])
@rate_limit(rate='5/m')
def initiate_chat_doctor_patient(request):

    try :
        appointment_id = request.GET.get('appointment_id')
        customer_id = request.GET.get('customer_id')

        if not appointment_id:
            return JsonResponse({'error': 'Appointment ID is required'}, status=400)
        if not customer_id:
            return JsonResponse({'error': 'Customer ID is required'}, status=400)

        appointment = get_object_or_404(AppointmentHeader, appointment_id=appointment_id)        
        doctor = appointment.doctor
        
        current_user = request.user
        if  current_user.is_staff:
            doctor_user = current_user
            customer_user = CustomerProfile.objects.get(id =customer_id).user
        else:
            customer_user = current_user
            doctor_user = doctor.user
        
     
        if appointment.appointment_status not in ['confirmed', 'completed']:
            return JsonResponse({'error': 'Appointment not confirmed'}, status=400)
        customer_user = get_object_or_404(CustomerProfile , id = customer_id)
       
        if appointment.doctor.user != doctor_user:
            return JsonResponse({'error': 'Not authorized for this appointment'}, status=403)
        chat_session = ChatSession.objects.create(
            created_by='doctor',
            description=f"Doctor chat with patient for appointment id: {appointment_id}",
            expires_at=timezone.now() + timedelta(hours=24)  # Session expires in 7 days
        )
        session_user = SessionUser.objects.create(
            session=chat_session,
            user=doctor_user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        session_user_patient = SessionUser.objects.create(
            session=chat_session,
            user=customer_user.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24))

        Message.objects.create(
            session=chat_session,
            sender=doctor_user,
            content=f"Doctor chat with patient for appointment id: {appointment_id}")

        return Response("successfully initiated chat")

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


    


@api_view(['GET'])
@rate_limit(rate='5/m')
@permission_classes([IsAuthenticated])
def initiate_chat_doctor_admin(request):
    try :
        current_user = request.user
        if  current_user.is_superuser:
            admin_user = current_user
            doctor_user = DoctorProfiles.objects.get(doctor_profile_id = request.GET.get('doctor_id')).user
        else:
            doctor_user = current_user
            admin_user = User.objects.get(username = '7483963192')

        chat_session = ChatSession.objects.create(
            created_by='doctor',
            description=f"Doctor chat with admin",
            expires_at=timezone.now() + timedelta(hours=24)  # Session expires in 7 days
        )
        session_user = SessionUser.objects.create(
            session=chat_session,
            user=doctor_user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        session_user_admin = SessionUser.objects.create(
            session=chat_session,
            user=admin_user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24))

        Message.objects.create(
            session=chat_session,
            sender=doctor_user,
            content=f"Doctor chat with admin")
        return Response("successfully initiated chat")
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@rate_limit(rate='5/m')
@permission_classes([IsAuthenticated])
def initiate_chat_patient_admin(request):
    try :
        
        current_user = request.user
        if  current_user.is_superuser:
            admin_user = current_user
            patient_user = CustomerProfile.objects.get(id = request.GET.get('customer_id')).user
        else:
            patient_user = current_user
            admin_user = User.objects.get(username = '7483963192')
        
        chat_session = ChatSession.objects.create(
            created_by='patient',
            description=f"Patient chat with admin",
            expires_at=timezone.now() + timedelta(hours=24)  # Session expires in 7 days
        )
        session_user = SessionUser.objects.create(
            session=chat_session,
            user=patient_user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        session_user_admin = SessionUser.objects.create(
            session=chat_session,
            user=admin_user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24))
        Message.objects.create(
            session=chat_session,
            sender=patient_user,
            content=f"Patient chat with admin")

        return Response({"message": "Chat session created successfully", "session_id": chat_session.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)












@require_GET
@validate_session_token
@rate_limit(rate='10/m')
@login_required
def join_chat(request, session_user):
    """
    Secure version of join chat with:
    - Authentication requirement
    - Token validation
    - Rate limiting
    - Session validation
    """
    try:
        session = session_user.session
        messages = session.messages.all().order_by('timestamp')
        
        # Get user profile information securely
        profile_data = {}
        if request.user.is_superuser:
            profile_data['admin'] = "Inticure"
        elif hasattr(request.user, 'doctorprofiles'):
            profile_data['doctor'] = request.user.doctorprofiles.first_name
        elif hasattr(request.user, 'customerprofile'):
            profile_data['customer'] = request.user.first_name  # Using first_name from user model

        # Set secure cookie for session
        response = render(request, 'chat_box.html', {
            'session': session,
            'token': session_user.token,
            'messages': messages,
            'session_user': session_user,
            **profile_data
        })
        
        response.set_cookie(
            'chat_session_token', 
            session_user.token,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=True,
            samesite='Strict'
        )
        
        return response

    except Exception as e:
        return JsonResponse({'error': 'Unable to join chat'}, status=500)
    


























from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Max
from .models import ChatSession, SessionUser, Message
from .utils import rate_limit
from doctor.models import DoctorProfiles
from customer.models import CustomerProfile

User = get_user_model()

# @rate_limit(rate='10/m')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_active_chat_sessions(request):
    """
    Get all active chat sessions for a specific user
    
    Query Parameters:
    - user_id: The ID of the user to get sessions for
    - username: Alternative to user_id, get sessions by username
    - include_closed: (optional) Include closed sessions, default=False
    - limit: (optional) Limit number of results, default=20
    """
    try:
      
        include_closed = request.data.get('include_closed')
        limit = 20
        user = request.user
        session_query = Q(session_users__user=user)
        
        if not include_closed:
            session_query &= Q(is_open=True)
        
        session_query &= Q(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        
        sessions = ChatSession.objects.filter(session_query).distinct().annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-created_at')[:limit]
        
        sessions_data = []
        for session in sessions:
            # Get all participants in this session
            participants = []
            doctor_name = ''
            customer_name= ''
            session_users = SessionUser.objects.filter(session=session).select_related('user')
            
            for session_user in session_users:
                participant_user = session_user.user
                participant_info = {
                    'user_id': participant_user.id,
                    'username': participant_user.username,
                    'is_current_user': participant_user.id == user.id,
                    'is_active': session_user.is_active,
                    'joined_at': session_user.joined_at.isoformat() if session_user.joined_at else None
                }
                if participant_user.is_superuser:
                    participant_info['role'] = 'admin'
                    participant_info['display_name'] = 'Inticure Support'
                elif  DoctorProfiles.objects.filter(user=participant_user).exists():
                    doctor_profile = DoctorProfiles.objects.get(user=participant_user)
                    participant_info['role'] = 'doctor'
                    participant_info['display_name'] = doctor_profile.first_name or participant_user.username
                    participant_info['doctor_id'] = doctor_profile.doctor_profile_id
                    doctor_name = f"{doctor_profile.salutation} {doctor_profile.first_name} {doctor_profile.last_name}"
                elif CustomerProfile.objects.filter(user=participant_user).exists():
                    customer_profile = CustomerProfile.objects.get(user=participant_user)
                    participant_info['role'] = 'patient'
                    participant_info['display_name'] = participant_user.first_name or participant_user.username
                    participant_info['customer_id'] = customer_profile.id
                    customer_name=f"{customer_profile.user.first_name} {customer_profile.user.last_name}"
                else:
                    participant_info['role'] = 'user'
                    participant_info['display_name'] = participant_user.get_full_name() or participant_user.username
                
                participants.append(participant_info)
            
            # Get last message
            last_message = session.messages.order_by('-timestamp').first()
            last_message_data = None
            if last_message:
                sender_display_name ="you" if last_message.sender == user else get_user_display_name(last_message.sender)
                last_message_data = {
                    'id': last_message.id,
                    'content': last_message.content[:100] + ('...' if len(last_message.content) > 100 else ''),  # Truncate for preview
                    'sender_id': last_message.sender.id,
                    'sender_name': sender_display_name,
                    'timestamp': last_message.timestamp.isoformat(),
                    'is_from_current_user': last_message.sender.id == user.id
                }
            
            # Get unread message count for current user
            unread_count = Message.objects.filter(
                session=session,
                is_read=False
            ).exclude(sender=user).count()
            
            # Get current user's session token
            current_user_session = SessionUser.objects.filter(
                session=session, 
                user=user
            ).first()

            
            
            session_data = {
                'session_id': session.id,
                'description': customer_name if user.is_staff else doctor_name,
                'created_at': session.created_at.isoformat(),
                'closed_at': session.closed_at.isoformat() if session.closed_at else None,
                'is_open': session.is_open,
                'created_by': session.created_by,
                'expires_at': session.expires_at.isoformat() if session.expires_at else None,
                'participants': participants,
                'participant_count': len(participants),
                'last_message': last_message_data,
                'unread_count': unread_count,
                'user_token': str(current_user_session.token) if current_user_session else None,
                'can_join': current_user_session and current_user_session.is_active and (
                    not current_user_session.expires_at or current_user_session.expires_at > timezone.now()
                ),
                'chat_url': f'/chat/join/?session_id={session.id}&token={current_user_session.token}' if current_user_session else None
            }
            
            sessions_data.append(session_data)
        
        response_data = {
            'success': True,
            'user_id': user.id,
            'username': user.username,
            'total_sessions': len(sessions_data),
            'sessions': sessions_data,
            'filters_applied': {
                'include_closed': include_closed,
                'limit': limit
            }
        }
        
        return JsonResponse(response_data, status=200)
        
    except User.DoesNotExist:
        return JsonResponse({
            'error': 'User not found'
        }, status=404)
    except ValueError as e:
        return JsonResponse({
            'error': f'Invalid parameter: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Internal server error: {str(e)}'
        }, status=500)


def get_user_display_name(user):
    """
    Helper function to get appropriate display name for a user
    """
    try:
        if user.is_superuser:
            return "Inticure Support"
        
        if  DoctorProfiles.objects.filter(user=user).exists():
            doctor_profile = DoctorProfiles.objects.get(user=user)
            return doctor_profile.first_name 
        
        if CustomerProfile.objects.filter(user=user).exists():
            return user.first_name 
        
        return user.first_name
    except Exception:
        return user.username


@api_view(['GET'])
@rate_limit(rate='15/m')
# @permission_classes([IsAuthenticated])
def get_chat_session_detail(request, session_id):
    """
    Get detailed information about a specific chat session
    
    Path Parameters:
    - session_id: The ID of the chat session
    
    Query Parameters:
    - user_id or username: User requesting the session details
    """
    try:
        user_id = request.GET.get('user_id')
        username = request.GET.get('username')
        
        if not user_id and not username:
            return JsonResponse({
                'error': 'Either user_id or username is required'
            }, status=400)
        
        # Get the user
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = get_object_or_404(User, username=username)
        
        # Get the session
        session = get_object_or_404(ChatSession, id=session_id)
        
        # Check if user is authorized to view this session
        user_session = SessionUser.objects.filter(session=session, user=user).first()
        if not user_session:
            return JsonResponse({
                'error': 'Not authorized to view this session'
            }, status=403)
        
        # Get all messages in the session
        messages = session.messages.order_by('timestamp').select_related('sender')
        messages_data = []
        
        for message in messages:
            sender_display_name = get_user_display_name(message.sender)
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender.id,
                'sender_name': sender_display_name,
                'timestamp': message.timestamp.isoformat(),
                'is_from_current_user': message.sender.id == user.id,
                'is_read': message.is_read
            })
        
        # Get participants
        participants = []
        session_users = SessionUser.objects.filter(session=session).select_related('user')
        
        for session_user in session_users:
            participant_user = session_user.user
            participant_info = {
                'user_id': participant_user.id,
                'username': participant_user.username,
                'display_name': get_user_display_name(participant_user),
                'is_current_user': participant_user.id == user.id,
                'is_active': session_user.is_active,
                'joined_at': session_user.joined_at.isoformat() if session_user.joined_at else None
            }
            participants.append(participant_info)
        
        session_detail = {
            'session_id': session.id,
            'description': session.description,
            'created_at': session.created_at.isoformat(),
            'closed_at': session.closed_at.isoformat() if session.closed_at else None,
            'is_open': session.is_open,
            'created_by': session.created_by,
            'expires_at': session.expires_at.isoformat() if session.expires_at else None,
            'participants': participants,
            'messages': messages_data,
            'message_count': len(messages_data),
            'user_token': str(user_session.token),
            'can_send_messages': user_session.is_active and session.is_open and (
                not session.expires_at or session.expires_at > timezone.now()
            )
        }
        
        return JsonResponse({
            'success': True,
            'session': session_detail
        }, status=200)
        
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'error': 'Chat session not found'
        }, status=404)
    except User.DoesNotExist:
        return JsonResponse({
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Internal server error: {str(e)}'
        }, status=500)