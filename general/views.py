from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.utils.timezone import now
from uritemplate import api
from urllib3 import response
from administrator.models import PaymentEntries
from analysis.models import AppointmentHeader

import logging
logger = logging.getLogger(__name__)

# def consultation_cost_details_view(request):
#     entry = None
#     appointment_id = None

#     if request.method == 'POST':
#         appointment_id = request.POST.get('appointment_id')

#         try:
#             # Get the related appointment
#             entry = PaymentEntries.objects.get(appointment__appointment_id=appointment_id)
#         except PaymentEntries.DoesNotExist:
#             entry = None

#     return render(request, 'consultation_cost_details.html', {
#         'entry': entry,
#         'appointment_id': appointment_id
#     })



def consultation_cost_details_view(request):
 

    return render(request, 'price_calculator.html')











# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.http import HttpResponse
from datetime import datetime, timedelta
from .gmeet.gmeet import generate_google_meet
from .serializers import GoogleMeetEventSerializer

class GoogleMeetBackendView(APIView):
    def post(self, request):
        serializer = GoogleMeetEventSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            link = generate_google_meet(
                data['summary'],
                data['description'],
                # data['attendees'],      # ✅ fix: pass attendees
                data['start_time'],     # ✅ correct position
                data['end_time']        # ✅ correct position
            )
            return Response({"meet_link": link})
        return Response(serializer.errors, status=400)


from .gmeet.gmeet import fetch_meet_logs,fetch_meet_logs_with_meeting_code
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response


class Get_logs(APIView):
    def get(self, request):
        logs = []
        print('started log fetching')
        q_meeting_code = request.GET.get('meeting_code')
        for item in fetch_meet_logs():
            actor_email = item.get('actor', {}).get('email')
            event = item.get('events', [])[0]
            event_name = event.get('name')
            parameters = event.get('parameters', [])

            display_name = None
            identifier = actor_email
            start_timestamp = None
            duration_seconds = None
            meeting_code = None
            for param in parameters:
                name = param.get('name')
                if name == 'display_name':
                    display_name = param.get('value')
                elif name == 'identifier':
                    identifier = param.get('value')
                elif name == 'meeting_code':
                    meeting_code = param.get('value')
                elif name == 'start_timestamp_seconds':
                    start_timestamp = int(param.get('intValue'))
                elif name == 'duration_seconds':
                    duration_seconds = int(param.get('intValue'))
            if q_meeting_code:
                if q_meeting_code != meeting_code:
                    continue

            # Calculate joined and left time
            joined_at = None
            left_at = None
            if start_timestamp:
                # Already in UTC as utcfromtimestamp returns UTC time
                joined_at = datetime.utcfromtimestamp(start_timestamp).isoformat()
            if start_timestamp and duration_seconds:
                # Already in UTC as utcfromtimestamp returns UTC time
                left_at = datetime.utcfromtimestamp(start_timestamp + duration_seconds).isoformat()

            logs.append({
                'display_name': display_name,
                'identifier': identifier,
                'joined_at': joined_at,
                'left_at': left_at,
                'meeting_code':meeting_code
            })

        return Response( logs)





# from rest_framework.response import Response
# from rest_framework.views import APIView

# class Get_logs(APIView):

#     def get(self, request):
#         logs_data = []

#         for item in fetch_meet_logs():
#             event = item.get('events', [{}])[0]
#             event_name = event.get('name')
#             user = item.get('actor', {}).get('email')
#             parameters = event.get('parameters', [])

#             logs_data.append({
#                 'user': user,
#                 'event': event_name,
#                 'parameters': parameters
#             })

#         return Response({'logs': logs_data})

















from analysis.models import Meeting_Tracker
from .utils import seconds_until_in_timezone
from django.utils import timezone

# class Map_Meetings(APIView):
#     def get(self, request,attendee_meeting_id):
#         print(attendee_meeting_id)
#         print("4a6f5241-529d-4e84-bd6d-cdd601f51b3a" == attendee_meeting_id)
#         context = False 
#         meeting_tracker = Meeting_Tracker.objects.filter(
#             customer_1_meeting_id = "4a6f5241-529d-4e84-bd6d-cdd601f51b3a"
#         ).first()
#         join = request.GET.get('join')
        
#         if meeting_tracker:
#             if join:
#                 if  meeting_tracker.appointment.start_time-timedelta(minutes=5) <= timezone.now() :
#                     meeting_tracker.customer_1_joined = True
#                     meeting_tracker.save()
#                     return redirect(meeting_tracker.meeting_link)
#             context = {
#                 'username': meeting_tracker.customer_1.user.first_name,
#                 'time_left_to_start': seconds_until_in_timezone(meeting_tracker.appointment.start_time , meeting_tracker.customer_1.time_zone),  # 10 minutes in seconds - change this to test different scenarios
#                 'meet_link':  meeting_tracker.customer_1_meeting_link ,
#                 'is_customer': True
#             }

#         meeting_tracker = Meeting_Tracker.objects.filter(
#             customer_2_meeting_id = attendee_meeting_id
#         ).first()
#         if meeting_tracker:
#             if join:
#                 if  meeting_tracker.appointment.start_time-timedelta(minutes=5) <= timezone.now() :
#                     meeting_tracker.customer_2_joined = True
#                     meeting_tracker.save()
#                     return redirect(meeting_tracker.meeting_link)

#             context = {
#                 'username': meeting_tracker.customer_2.user.first_name,
#                 'time_left_to_start': seconds_until_in_timezone(meeting_tracker.appointment.start_time , meeting_tracker.customer_1.time_zone),  # 10 minutes in seconds - change this to test different scenarios
#                 'meet_link': meeting_tracker.customer_2_meeting_link,
#                 'is_customer': True
#             }


#         meeting_tracker = Meeting_Tracker.objects.filter(
#             doctor_meeting_id = attendee_meeting_id
#         ).first()
#         if meeting_tracker:
#             if join:
#                 if  meeting_tracker.appointment.start_time-timedelta(minutes=5) <= timezone.now() :
#                     meeting_tracker.doctor_joined = True
#                     meeting_tracker.save()
#                     return redirect(meeting_tracker.meeting_link)

#             context = {
#                 'username': meeting_tracker.appointment.doctor.first_name,
#                 'time_left_to_start': seconds_until_in_timezone(meeting_tracker.appointment.start_time , meeting_tracker.appointment.doctor.time_zone),  # 10 minutes in seconds - change this to test different scenarios
#                 'meet_link': meeting_tracker.doctor_meeting_link,  
#             }

#         if context:

#             return render(request, 'meet/join.html', context)




#         return Response({
#             'message': 'Meeting not found'
#         })
    

class Map_Meetings(APIView):
    def get(self, request,attendee_meeting_id):
        logger.debug(attendee_meeting_id)
        logger.debug("4a6f5241-529d-4e84-bd6d-cdd601f51b3a" == attendee_meeting_id)
        context = False 
        meeting_tracker = Meeting_Tracker.objects.filter(
            customer_1_meeting_id = attendee_meeting_id
        ).first()
        join = request.GET.get('join')
        
        if meeting_tracker:
            if join:
                if  meeting_tracker.appointment.start_time-timedelta(minutes=5) <= timezone.now() :
                    meeting_tracker.customer_1_joined = True
                    meeting_tracker.save()
                    return redirect(meeting_tracker.meeting_link)
            context = {
                'salutation':meeting_tracker.appointment.doctor.salutation,
                'doctor_name':f"{meeting_tracker.appointment.doctor.first_name} {meeting_tracker.appointment.doctor.last_name}",
                "time":meeting_tracker.appointment.start_time.time(),
                "date":meeting_tracker.appointment.start_time.date(),
                'specialization':meeting_tracker.appointment.specialization.specialization,
                'username': meeting_tracker.customer_1.user.first_name,
                'time_left_to_start': seconds_until_in_timezone(meeting_tracker.appointment.start_time , meeting_tracker.customer_1.time_zone),  # 10 minutes in seconds - change this to test different scenarios
                'meet_link':  meeting_tracker.customer_1_meeting_link ,
                'meet_code': meeting_tracker.meeting_code,  
                'is_customer': True
            }

        meeting_tracker = Meeting_Tracker.objects.filter(
            customer_2_meeting_id = attendee_meeting_id
        ).first()
        if meeting_tracker:
            if join:
                if  meeting_tracker.appointment.start_time-timedelta(minutes=5) <= timezone.now() :
                    meeting_tracker.customer_2_joined = True
                    meeting_tracker.save()
                    return redirect(meeting_tracker.meeting_link)

            context = {
                'salutation':meeting_tracker.appointment.doctor.salutation,
                'doctor_name':f"{meeting_tracker.appointment.doctor.first_name} {meeting_tracker.appointment.doctor.last_name}",
                "time":meeting_tracker.appointment.start_time.time(),
                "date":meeting_tracker.appointment.start_time.date(),
                'specialization':meeting_tracker.appointment.specialization.specialization,
                'username': meeting_tracker.customer_2.user.first_name,
                'time_left_to_start': seconds_until_in_timezone(meeting_tracker.appointment.start_time , meeting_tracker.customer_1.time_zone),  # 10 minutes in seconds - change this to test different scenarios
                'meet_link': meeting_tracker.customer_2_meeting_link,
                'meet_code': meeting_tracker.meeting_code,  
                'is_customer': True
            }


        meeting_tracker = Meeting_Tracker.objects.filter(
            doctor_meeting_id = attendee_meeting_id
        ).first()
        if meeting_tracker:
            if join:
                if  meeting_tracker.appointment.start_time-timedelta(minutes=5) <= timezone.now() :
                    meeting_tracker.doctor_joined = True
                    meeting_tracker.save()
                    return redirect(meeting_tracker.meeting_link)

            context = {
                'username': meeting_tracker.appointment.doctor.first_name,
                'time_left_to_start': seconds_until_in_timezone(meeting_tracker.appointment.start_time , meeting_tracker.appointment.doctor.time_zone),  # 10 minutes in seconds - change this to test different scenarios
                'meet_link': meeting_tracker.doctor_meeting_link,  
                'meet_code': meeting_tracker.meeting_code,  
                'salutation':meeting_tracker.appointment.doctor.salutation,
                'doctor_name':f"{meeting_tracker.appointment.doctor.first_name} {meeting_tracker.appointment.doctor.last_name}",
                "time":meeting_tracker.appointment.start_time.time(),
                "date":meeting_tracker.appointment.start_time.date(),
                'specialization':meeting_tracker.appointment.specialization.specialization,
            }


        if context:

            # return redirect(f'inticure.com/meet/?doctor_name={context["doctor_name"]}&salutation={context["salutation"]}&start_time={context["start_time"]}&specialization={context["specialization"]}&username={context["username"]}&time_left_to_start={context["time_left_to_start"]}&meet_link={context["meet_link"]}&is_customer={context.get("is_customer", False)}')
            # return redirect(f"https://inticure.com/join-meeting?dr={context['salutation']}%20{context['doctor_name']}&date={context['date']}&time={context['time']}&meetingId={context['meet_code']}{f"&specialization={context['specialization']}" if context['specialization']!="No Specialization" else ""}")
            specialization = f"&specialization={context['specialization']}" if context['specialization'] != "No Specialization" else ""

            # return redirect(
            #     f"https://inticure.com/join-meeting?"
            #     f"dr={context['salutation']}%20{context['doctor_name']}"
            #     f"&date={context['date']}"
            #     f"&time={context['time']}"
            #     f"&meetingId={context['meet_code']}"
            #     f"{specialization}"
            # )
            if meeting_tracker.appointment.start_time-timedelta(seconds=30)<=timezone.now():
                return redirect(meeting_tracker.meeting_link)

        return Response({
            'message': 'Meeting not found'
        })
    

from django.shortcuts import render
from django.http import HttpResponse
import datetime

def meeting_waiting_room(request):
  
    context = {
        'username': 'John Doe',  # Example username
        'time_left_to_start': 600,  # 10 minutes in seconds - change this to test different scenarios
        'meet_link': 'https://meet.example.com/room-123',  # Example meeting link
    }
    
    # For testing different scenarios, you could add URL parameters:
    # Example: /waiting-room?time_left=300
    time_left_param = request.GET.get('time_left')
    if time_left_param and time_left_param.isdigit():
        context['time_left_to_start'] = int(time_left_param)
    
    return render(request, 'meet/join.html', context)





        
from .emal_service import *

class Email_tester(APIView):
    def get(self, request):
       
        # context = {
        # "email": 'user',
        # "year": datetime.now().year,
        # 'backend_url':BACKEND_URL,  
        # }

        return render(request, 'meet/new.html')

        
    

        return Response('sfoih')
    


class Email_tester2(APIView):
    def get(self, request):
        subject = "Verify Your Email - Inticure"

        context = {
            "name": "joel",
            "otp": '123456',
            'year':timezone.now().year,
            'backend_url':BACKEND_URL,  
        }

        html_content = render_to_string("email_otp.html", context)

        send_email_via_sendgrid(subject, html_content, "joelbaiju98@gmail.com")

        return Response("ssfs")


















from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

# Your verify token (should match the one in Facebook Developer settings)
WHATSAPP_VERIFY_TOKEN = "KSS4SQMQuCmh9Z9BU9GWv8Cjlm7FTt0SKOKKDlSXFjUdW2qgOQImHZ1xRJ0LOwovjMKa49tuxPbUdWGf0v9dHk5WuKpVWBevLruXJm2iCQsrz6s4BldoiQveQPuwEBuBw9muxl0eGo5byfM5LBvUg"  # Replace with your actual token

@api_view(['GET', 'POST'])
def whatsapp_callback(request):
    # Handle verification request (GET)
    if request.method == 'GET':
        # Extract verification parameters
        hub_mode = request.GET.get('hub.mode')
        hub_token = request.GET.get('hub.verify_token')
        hub_challenge = request.GET.get('hub.challenge')
        
        # Verify the token
        if hub_mode == 'subscribe' and hub_token == WHATSAPP_VERIFY_TOKEN:
            print("Webhook verified successfully")
            return Response(int(hub_challenge), status=status.HTTP_200_OK)
        else:
            print("Webhook verification failed")
            return Response("Verification failed", status=status.HTTP_403_FORBIDDEN)
    
    # Handle incoming messages (POST)
    elif request.method == 'POST':
        try:
            data = request.data
            print("Received webhook data:", json.dumps(data, indent=2))
            
            # Process different types of updates
            if 'object' in data and data['object'] == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        field = change.get('field')
                        value = change.get('value')
                        
                        # Handle messages
                        if field == 'messages':
                            print("New message received:", value)
                            # Add your message processing logic here
                        
                        # Handle message status updates
                        elif field == 'message_status':
                            print("Message status update:", value)
                            # Add your status handling logic here
            
            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            print("Error processing webhook:", str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)








from .whatsapp.whatsapp_messages import *
from .notification_controller import send_appointment_confirmation_notification

@api_view(["GET"])
def swtm_view(request):
    # result = send_wa_appointment_confirmation(
    #     to_phone="917034761676",
    #     patient_name="John Doe",
    #     salutation="Dr.",
    #     specialist_name="Smith",
    #     date_time="2024-10-01 10:00 AM",
    #     meet_link="https://meet.example.com/appointment123"
    # )    
    # result = send_wa_consultation_reminder_24_hours_before(
    #     to_phone="917034761676",
    #     patient_name="John Doe",
    #     salutation="Dr.",
    #     specialist_name="Smith",
    #     date_time="2024-10-01 10:00 AM",
    #     meet_code="123654789"
    # )


    # result = send_wa_consultation_reminder_1_hour_before(
    #     to_phone="917034761676",
    #     patient_name="John Doe",
    #     salutation="Dr.",
    #     specialist_name="Smith",
    #     date_time="2024-10-01 10:00 AM",
    #     meet_code="123654789"
    # )
    logger.info("Creating meeting tracker for appointment %s", 109)


    result = send_appointment_confirmation_notification(
       appointment_id=109
    )
    logger.debug(result)


    # result = send_wa_auth_code(to_phone="917034761676", auth_code="123456")
    return Response(result) 




from .models import CommonFileUploader
from customer.models import CustomerProfile
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file_view(request):
    if request.method == 'POST' and request.FILES.get('common_file'):
        uploaded_file = request.FILES['common_file']
        if uploaded_file.size > 10 * 1024 * 1024:  # 10 MB limit
            return Response({'error': 'File size exceeds 10 MB limit'}, status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            return Response({'error': 'Invalid file type. Only PDF and image files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.POST.get('appointment_id') :
            return Response({'error': 'appointment_id and file_name are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_staff:
            customerprofile = CustomerProfile.objects.get(user=request.user)
        else:
            customerprofile = None
        file_instance = CommonFileUploader.objects.create(
            appointment_id=request.POST.get('appointment_id'),
            common_file=uploaded_file,
            file_name=request.POST.get('file_name'),
            customer=customerprofile,
            uploaded_by_doctor = True if request.user.is_staff else False
        )

        return Response({'message': 'File uploaded successfully', 'file_id': file_instance.id}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)