from rest_framework.decorators import api_view
from rest_framework.response import Response
from administrator.models import LanguagesKnown,Countries , Specializations
from administrator.serializers import LanguagesKnownSerializer, CountriesSerializer ,SpecializationsSerializer
from inticure_prime_backend.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from general.models import Phone_OTPs , Email_OTPs
from general.utils import send_otp_email 
from general.twilio import send_otp_sms
from general.utils import generate_random_otp
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes






@api_view(['GET'])
def get_all_languages(request):
    languages = LanguagesKnown.objects.all()
    serializer = LanguagesKnownSerializer(languages, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_countries(request):
    countries = Countries.objects.all()
    serializer = CountriesSerializer(countries, many=True)
    return Response(serializer.data)


from datetime import timedelta

@api_view(['GET'])
def get_all_specializations(request):
    session_type = request.GET.get('is_couple')
    print(f"Session type received: {session_type}")
    if session_type and session_type.lower() == 'true':
        print(f"Fetching specializations with double session duration {session_type}")
        specializations = Specializations.objects.filter(
            double_session_duration__isnull=False,
            double_session_duration__gt=timedelta(seconds=0)
        )
    else:
        specializations = Specializations.objects.all()
    serializer = SpecializationsSerializer(specializations, many=True)
    return Response(serializer.data)

class LoginView(APIView):
    def get_serializer_class(self):
        return None
    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email_id')
        country_code = request.data.get('country_code', '+91')  

        # otp = generate_random_otp()
        otp = 666666

        if phone_number:
            if not DoctorProfiles.objects.filter(mobile_number = phone_number).exists():
                return Response('The provided mobile number is not connected with any account',status=status.HTTP_400_BAD_REQUEST)

            print("Phone number received and got in:", phone_number)
            otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = otp)
            send_otp_sms(otp = otp_instance.otp , to_number=country_code+phone_number)
            print("OTP sent to phone number:", phone_number)
            
        if email:
            if not DoctorProfiles.objects.filter(email_id = email).exists():
                return Response('The provided email id is not connected with any account',status=status.HTTP_400_BAD_REQUEST)

            otp_instance = Email_OTPs.objects.create(email=email, otp=otp)
            send_otp_email(otp = otp_instance.otp , toemail=email , firstname = 'user')
            print("OTP sent to email:", email)
        
            print(otp_instance.otp)

        
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'email': email
        }) 



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class Verify_Login(APIView):
    def get_serializer_class(self):
        return None

    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email_id')
        otp = request.data.get('otp')

        if not otp or (not phone_number and not email):
            return Response( 'Phone number or email and OTP are required.', status=HTTP_400_BAD_REQUEST)


        
        user = None
        doctor_profile = None

        # Phone OTP verification
       # Phone OTP verification
        if phone_number:
            try:
                phone_otp = Phone_OTPs.objects.filter(phone=phone_number, otp=otp).order_by('-created_at').first()
                if not phone_otp:
                    return Response('Invalid OTP for phone number', status=HTTP_400_BAD_REQUEST)

                doctor_profile = DoctorProfiles.objects.get(mobile_number=phone_number)
                user = User.objects.filter(username=phone_number).first()

            except DoctorProfiles.DoesNotExist:
                return Response('Account not found, Invalid phone number', status=HTTP_400_BAD_REQUEST)

        # Email OTP verification
        if email:
            try:
                email_otp = Email_OTPs.objects.filter(email=email, otp=otp).order_by('-created_at').first()
                if not email_otp:
                    return Response('Invalid OTP for email', status=HTTP_400_BAD_REQUEST)

                doctor_profile = DoctorProfiles.objects.get(email_id=email)
                user = User.objects.filter(email=email).first()

            except DoctorProfiles.DoesNotExist:
                return Response('Account not found, Invalid Email ID', status=HTTP_400_BAD_REQUEST)

        if doctor_profile.is_accepted:
            status='accepted'
        elif doctor_profile.rejected:
            status='rejected'
        else :
            status = "pending"
        if user:
           
            refresh = RefreshToken.for_user(user)
            return Response({
                'verified'      : True,
                'message'       : 'Existing user Verified',
                'did'           : doctor_profile.doctor_profile_id,
                'doctor_flag'   : doctor_profile.doctor_flag,
                'sessionid'     : str(refresh.access_token),
                'refresh_token' : str(refresh),
                'status'        :status
            }, status=HTTP_200_OK)

        else:
            # Create new user for doctor profile
            username = phone_number or email
            if not username:
                return Response('Username could not be determined.', status=HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                username=username,
                email=email if email else None,
                password=otp
            )
            doctor_profile.user = user
            doctor_profile.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'user_exists'   : False,
                'verified'      : True,
                'message'       : 'New user created and verified',
                'did'           : doctor_profile.doctor_profile_id,
                'doctor_flag'   : doctor_profile.doctor_flag,
                'sessionid'     : str(refresh.access_token),
                'refresh_token' : str(refresh),
                'status'        :status
            }, status=HTTP_200_OK)




from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import DoctorSpecializations,DoctorProfiles
from .serializers import *

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_doctor_profile(request):
    # Handle specializations[] manually
    specialization_ids = request.data.getlist('specializations[]')
    language_ids       = request.data.getlist('language_ids[]')

    # Copy other data to mutable form
    data = request.data.copy()

    # Pass to serializer (excluding specializations)
    mobile_number = request.data.get('mobile_number')
    email_id = request.data.get('email_id')

    if DoctorProfiles.objects.filter(mobile_number = mobile_number).exists():
        return Response('The provided mobile number is already connected with another account',status=status.HTTP_400_BAD_REQUEST)

    if DoctorProfiles.objects.filter(email_id = email_id).exists():
        return Response('The provided email id is already connected with another account',status=status.HTTP_400_BAD_REQUEST)


    serializer = DoctorProfileCreateSerializer(data=data)
    if serializer.is_valid():
        doctor_profile = serializer.save()

        # Add doctor specializations
        for spec_id in specialization_ids:
            DoctorSpecializations.objects.create(
                doctor=doctor_profile,
                specialization_id=int(spec_id)
            )
        for lid in language_ids:
            if LanguagesKnown.objects.get(id=lid).language=="English":
                continue
            DoctorLanguages.objects.create(
                doctor=doctor_profile,
                language_id=int(lid)
            )
        DoctorLanguages.objects.create(
            doctor=doctor_profile,
            language=LanguagesKnown.objects.get(language = "English")
        )
        

        


        return Response('Doctor profile created successfully', status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)











from customer.serializers import CustomerProfileSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        user = request.user
        try:
            doctor = DoctorProfiles.objects.get(user=user)
        except DoctorProfiles.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)
        
        data = {}
        data['doctor_details'] = DoctorProfileSerializer_Dashboard(doctor)
        appointments = {}
        appointments['todays_appointments'] = AppointmentHeader
        
        



@api_view(['GET'])
def dotor_details_from_id(request):
    # Use GET or POST depending on your frontend/client
    did = request.GET.get('did') 

    if not did:
        return Response({"error": "did is required"}, status=400)

    try:
        doctor = DoctorProfiles.objects.get(doctor_profile_id=did)
    
        if doctor.is_accepted:
            status='accepted'
        elif doctor.rejected:
            status='rejected'
        else :
            status = "pending"
        res = {
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "email_id": doctor.email_id,    \
            "phone":doctor.mobile_number,
            "joined_date": doctor.joined_date,
            "status" : status                                                                                       
        }
        return Response(res, status=200)
    
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=400)
    










from datetime import date, datetime, time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from datetime import datetime, date, timedelta, time
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status




from datetime import datetime, date as dt_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from .models import DoctorProfiles, Calendar, DoctorAvailableHours
from .serializers import DoctorAvailableHoursSerializer


class DoctorAvailableHoursView(APIView):
    """
    GET  /api/doctor/available-hours/?date=YYYY-MM-DD  → list blocks for that date (or today if not passed)
    POST /api/doctor/available-hours/ → add a time block for a date
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.GET.get('date')

        try:
            doctor = DoctorProfiles.objects.get(user=request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=404)

        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else dt_date.today()
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            calendar = Calendar.objects.get(date=query_date)
        except Calendar.DoesNotExist:
            return Response({"detail": f"No calendar entry found for date {query_date}."},
                            status=status.HTTP_404_NOT_FOUND)

        hours_qs = DoctorAvailableHours.objects.filter(
            doctor=doctor,
            date=calendar
        ).order_by('start_time')

        data = [
            {
                "date": calendar.date.isoformat(),
                "start_time": entry.start_time.strftime("%H:%M"),
                "end_time": entry.end_time.strftime("%H:%M"),
            }
            for entry in hours_qs
        ]

        return Response(data, status=status.HTTP_200_OK)

   
    @transaction.atomic
    def post(self, request):
        data = request.data
        dates = data.get("dates", [])
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")

        # Parse time strings to datetime.time objects
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except (TypeError, ValueError):
            return Response({"detail": "Invalid time format. Expected HH:MM."}, status=400)

        for date in dates:
            try:
                calendar = Calendar.objects.get(date=date)
            except Calendar.DoesNotExist:
                return Response({"detail": f"No calendar entry for {date}."}, status=404)

            try:
                doctor = DoctorProfiles.objects.get(user=request.user)
            except DoctorProfiles.DoesNotExist:
                return Response({"detail": "Doctor profile not found."}, status=404)

            # Prevent overlapping blocks
            overlap_exists = DoctorAvailableHours.objects.filter(
                doctor=doctor,
                date=calendar,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists()

            if overlap_exists:
                return Response(
                    {"detail": "Overlapping time block already exists for this date."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create availability block
            DoctorAvailableHours.objects.create(
                doctor=doctor,
                date=calendar,
                start_time=start_time,
                end_time=end_time
            )

        return Response(
            {
                "message": "Availability block saved successfully.",
                "dates": dates,
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
            },
            status=status.HTTP_201_CREATED
        )



# views/appointments.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from .slots_service import get_available_slots









from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import datetime, date as dt_date
from .models import DoctorProfiles,DoctorAppointment
from general.models import PreTransactionData
from analysis.models import AppointmentHeader
from collections import defaultdict


from customer.models import CustomerProfile
from customer.models import Extra_questions_answers
from analysis.models import Observation_Notes
class Customer_details_update(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        appointment_id = data.get('appointment_id')
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
            customer = appointment.customer
            message = ""
            if data.get('weight'):
                customer.weight = data.get('weight')
                customer.weight_unit = data.get('weight_unit')
                message = "Weight"
            if data.get('height'):
                customer.height = data.get('height')
                customer.height_unit = data.get('height_unit')
                message = message + "Height"
            if data.get('note'):
                note = Observation_Notes.objects.create(note = data.get('note') ,appointment = appointment )
            customer.save()


            if data.get('extra_questions'):
                for question in data.get('extra_questions'):
                    Extra_questions_answers.objects.create(question_id=question.get('question_id'), answer=question.get('answer'), customer=customer)
                message = message + "Extra questions"

            message = message + " updated successfully."
            return Response({"message": message}, status=status.HTTP_200_OK)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
    
from .serializers import ExtraQuestionsSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict
from datetime import datetime, date as dt_date, timedelta
from django.db.models import Sum
from django.db.models import Q


class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            doctor = DoctorProfiles.objects.get(user=request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=404)

        today = dt_date.today()

        # Earnings today
        earnings_qs = PreTransactionData.objects.filter(
            appointment__doctor=doctor,
            appointment__appointment_date=today
        ).aggregate(total=Sum("total_amount"))
        earnings_today = earnings_qs["total"] or 0

        # Earnings change (compared to yesterday)
        yesterday = today - timedelta(days=1)
        earnings_yesterday_qs = PreTransactionData.objects.filter(
            appointment__doctor=doctor,
            appointment__appointment_date=yesterday
        ).aggregate(total=Sum("total_amount"))
        earnings_yesterday = earnings_yesterday_qs["total"] or 0

        if earnings_yesterday > 0:
            earnings_change = round(((earnings_today - earnings_yesterday) / earnings_yesterday) * 100, 2)
        else:
            earnings_change = 0.0

        # Appointments today (based on confirmation + incomplete)
        appointments = DoctorAppointment.objects.filter(
            doctor=doctor,
            confirmed=True,
            completed=False
        )
        total_appointments = appointments.count()
        completed = appointments.filter(completed=True).count()
        pending = total_appointments - completed

        # Doctor info
        specialization_qs = doctor.doctor_specializations.all()
        specialization_names = ", ".join([spec.specialization.specialization for spec in specialization_qs]) if specialization_qs else "no specialization"

        doctor_info = {
            "name": f"Dr. {doctor.first_name} {doctor.last_name}",
            "specialization": specialization_names,
            "experience": doctor.experience if doctor.experience else "N/A",
            "rating": 4.9  # Placeholder
        }

       
        now = datetime.now()
        today = now.date()
        current_time = now.time()

        upcoming = DoctorAppointment.objects.filter(
            doctor=doctor,
            confirmed=True,
            completed=False
        ).filter(
            Q(date__date=today, start_time__gte=current_time) |
            Q(date__date__gt=today)
        ).order_by("date__date", "start_time")[:3]

        print(now.time)
        # Group upcoming by specialization
        uapp=[]
        for appt in upcoming:
            customer_name = appt.appointment.customer.user.first_name + " " + appt.appointment.customer.user.last_name if appt.appointment and appt.appointment.customer else "Unknown"
            appt_type = "Couple" if appt.appointment and appt.appointment.is_couple else "Individual"
            time_str = appt.start_time.strftime("%I:%M %p") if appt.start_time else "N/A"
            if appt.start_time and appt.end_time:
                duration_minutes = int(
                    (datetime.combine(today, appt.end_time) - datetime.combine(today, appt.start_time)).total_seconds() // 60
                )
                duration = f"{duration_minutes} mins"
            else:
                duration = "Unknown"

            spec_name = appt.specialization.specialization if appt.specialization else "General"

            uapp.append({
                "appointment_id": appt.appointment.appointment_id if appt.appointment else None,
                "name": customer_name,
                "type": appt_type,
                "time": time_str,
                "duration": duration,
                "specialization": spec_name,
                "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
                "followup": True if appt.appointment and appt.appointment.followup_id else False,
                "meeting_link": appt.appointment.meeting_link if appt.appointment else None,
                "date": appt.date.date.strftime("%Y-%m-%d") if appt.date else None
            })

     

        # Final response
        return Response({
            "earnings_today": earnings_today,
            "earnings_change": earnings_change,
            "appointments_today": {
                "total": total_appointments,
                "completed": completed,
                "pending": pending
            },
            "doctor_info": doctor_info,
            "upcoming_appointments": uapp
        })











class GetAppointmentsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            doctor = DoctorProfiles.objects.get(user=request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=404)

        today = dt_date.today()

        # Earnings today
      
        # Appointments today (based on confirmation + incomplete)
        appointments = DoctorAppointment.objects.filter(
            doctor=doctor,
            confirmed=True,
            completed=False
        )
   

       
        now = datetime.now()
        today = now.date()
        current_time = now.time()

        upcoming = DoctorAppointment.objects.filter(
            doctor=doctor,
            confirmed=True,
            completed=False
        ).filter(
            Q(date__date=today, start_time__gte=current_time) |
            Q(date__date__gt=today)
        ).order_by("date__date", "start_time")[:3]

      
        uapp=[]
        for appt in upcoming:
            customer_name = appt.appointment.customer.user.first_name + " " + appt.appointment.customer.user.last_name if appt.appointment and appt.appointment.customer else "Unknown"
            appt_type = "Couple" if appt.appointment and appt.appointment.is_couple else "Individual"
            time_str = appt.start_time.strftime("%I:%M %p") if appt.start_time else "N/A"
            if appt.start_time and appt.end_time:
                duration_minutes = int(
                    (datetime.combine(today, appt.end_time) - datetime.combine(today, appt.start_time)).total_seconds() // 60
                )
                duration = f"{duration_minutes} mins"
            else:
                duration = "Unknown"

            spec_name = appt.specialization.specialization if appt.specialization else "General"

            uapp.append({
                "appointment_id": appt.appointment.appointment_id if appt.appointment else None,
                "name": customer_name,
                "type": appt_type,
                "time": time_str,
                "duration": duration,
                "specialization": spec_name,
                "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
                "followup": True if appt.appointment and appt.appointment.followup_id else False,
                "meeting_link": appt.appointment.meeting_link if appt.appointment else None,
                "date": appt.date.date.strftime("%Y-%m-%d") if appt.date else None
            })

     
        previos_appointments = []
        for appt in appointments:
            customer_name = appt.appointment.customer.user.first_name + " " + appt.appointment.customer.user.last_name if appt.appointment and appt.appointment.customer else "Unknown"
            appt_type = "Couple" if appt.appointment and appt.appointment.is_couple else "Individual"
            time_str = appt.start_time.strftime("%I:%M %p") if appt.start_time else "N/A"
            if appt.start_time and appt.end_time:
                duration_minutes = int(
                    (datetime.combine(today, appt.end_time) - datetime.combine(today, appt.start_time)).total_seconds() // 60
                )
                duration = f"{duration_minutes} mins"
            else:
                duration = "Unknown"

            spec_name = appt.specialization.specialization if appt.specialization else "General"

            previos_appointments.append({
                "appointment_id": appt.appointment.appointment_id if appt.appointment else None,
                "name": customer_name,
                "type": appt_type,
                "time": time_str,
                "duration": duration,
                "specialization": spec_name,
                "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
                "followup": True if appt.appointment and appt.appointment.followup_id else False,
                "meeting_link": appt.appointment.meeting_link if appt.appointment else None,
                "date": appt.date.date.strftime("%Y-%m-%d") if appt.date else None
            })
        # Final response
        return Response({
            "upcoming_appointments": uapp,
            "previous_appointments": previos_appointments
        })










class ReferralCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        try:
            customer = AppointmentHeader.objects.get(appointment_id=appointment_id).customer
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor = DoctorProfiles.objects.get(user=request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['customer'] = customer.id
        data['doctor'] = doctor.doctor_profile_id
        print(data)
        serializer = ReferralSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Referral created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





from .slots_service import get_preferred_doctors
from .slots_service import get_preferred_doctors
from django.core.serializers.json import DjangoJSONEncoder
import json

class FilterDoctorsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        appointment_id = data.get('appointment_id')
        specialization_id = data.get('specialization_id')
        language_info = data.get('language_info', {})
        gender_info = data.get('gender_info', {})
        date_str = data.get('date')
        is_couple = data.get('is_couple', False)
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
            appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()
            
            if not specialization:
                return Response({"error": "Invalid specialization ID"}, status=400)
            if not appointment:
                return Response({"error": "Invalid appointment ID"}, status=400)
                
        except ValueError:
            return Response({"error": "Invalid date format"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        session_duration_field = (
            specialization.double_session_duration if is_couple else specialization.single_session_duration
        )
        if session_duration_field is None:
            return Response({"error": "Session duration not defined."}, status=400)

        preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
            specialization=specialization.specialization,
            language_info=language_info,
            gender_info=gender_info,
            country=appointment.customer.country_details.country_name,
            flag='senior'
        )


        if not preferred_doctors:
                fallback_reason = fallback_reason or "No doctors available with preferrences. Showing all available doctors."
         
                preferred_doctors = DoctorProfiles.objects.filter(
                    doctor_flag='senior',
                    is_accepted=True,
                    payment_assignments__country__country_name=appointment.customer.country_details.country_name,
                ).distinct()


        preferred_doctors_available_in_date = preferred_doctors.filter(
            doctor_available_hours__date__date=date
        ).distinct()

        result = [{
            "id": doctor.doctor_profile_id,
            "name": f"{doctor.first_name} {doctor.last_name}",
            "gender": doctor.gender,
            "flag": doctor.doctor_flag,
            "specializations": [spec.specialization.specialization for spec in doctor.doctor_specializations.all()],
            "languages": [lang.language.language for lang in doctor.known_languages.all()],
            "profile_pic": doctor.profile_pic.url if doctor.profile_pic else None,  # Ensure this is a string URL
        } for doctor in preferred_doctors_available_in_date]

        response_data = {
            "available_doctors": result,
            "gender_matched": gender_matched,
            "language_matched": language_matched,
            "fallback_reason": fallback_reason
        }

        # Ensure all data is serializable
        try:
            json.dumps(response_data, cls=DjangoJSONEncoder)
        except TypeError as e:
            return Response({"error": f"Data serialization error: {str(e)}"}, status=500)

        return Response(response_data, status=200)
    


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def Get_availableSlots_docid(request):
    doctor_id = request.data.get('doctor_id')
    date_str = request.data.get('date')
    
    if not doctor_id:
        return Response({"error": "doctor_id is required"}, status=400)

    try:
        doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
    else:
        date_obj = datetime.now().date() + timedelta(days=1)  # Default to tomorrow

    slots = get_available_slots(doctor_id=doctor_id, date=date_obj)

    return Response({"slots": slots}, status=200)



from general.gmeet.gmeet import generate_google_meet
from analysis.tasks import delete_unpaid_appointment
from analysis.serializers import AppointmentHeaderSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Create_NewAppointment(request):
    if request.method == 'POST':
        slot = request.data.get('slot')
        doctor_id = request.data.get('doctor')
        appointment_id = request.data.get('appointment_id')
        appointment_date = request.data.get('appointment_date')
        language_pref = request.data.get('language_pref')
        gender_pref = request.data.get('gender_pref')
        specialization_id = request.data.get('specialization')
        is_couple = request.data.get('is_couple', False)
    

        try:
            o_appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
            customer = o_appointment.customer
            specialization  = Specializations.objects.get(specialization_id=specialization_id)


            print(slot)
            print(appointment_date,slot.get('start'))
            print(language_pref)
            slot_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            from_time = datetime.strptime(slot.get('start'), "%H:%M:%S").time()
            to_time = datetime.strptime(slot.get('end'), "%H:%M:%S").time()
            doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)

            overlapping = DoctorAppointment.objects.filter(
                doctor=doctor,
                date__date=slot_date,
                start_time__lt=to_time,
                end_time__gt=from_time
            ).exists()
            if overlapping:
                return Response({'error': 'The selected time slot overlaps with an existing appointment.'}, status=409)

            # Create new appointment
            appointment = AppointmentHeader.objects.create(
                    customer                = customer,
                    category                = o_appointment.category,
                    gender_pref             = gender_pref.get('value'),
                    appointment_status      = "pending_paymet",
                    status_detail           = "initiated by doctor waiting for payment",
                    confirmation_method     = request.data.get('confirmation_method'),
                    confirmation_phone_number= request.data.get('phone_number') if request.data.get('confirmation_method') in ["SMS", "WhatsApp"] else None,
                    confirmation_email      = request.data.get('email') if request.data.get('confirmation_method') == "Email" else None,
                    appointment_date        = slot_date,
                    appointment_time        = from_time,
                    doctor                  = doctor,
                    customer_message        = request.data.get('message'),
                    language_pref           = language_pref.get('value'),
                    specialization          = specialization,
                    is_couple               = is_couple,
            )

            # Generate meet link
            aware_from = timezone.make_aware(datetime.combine(slot_date, from_time))
            aware_to = timezone.make_aware(datetime.combine(slot_date, to_time))
            appointment.meeting_link = generate_google_meet(
                summary='Appointment',
                description='Appointment with doctor',
                start_time=aware_from,
                end_time=aware_to
            )
            appointment.save()

            DoctorAppointment.objects.create(
                doctor=doctor,
                specialization=specialization,
                date=Calendar.objects.get_or_create(date=slot_date)[0],
                start_time=from_time,
                end_time=to_time,
                appointment=appointment,
            )
            
            # delete_unpaid_appointment.apply_async((appointment.appointment_id,), countdown=300)

            return Response({
                'message': 'Appointment successfully booked',
                'appointment': AppointmentHeaderSerializer(appointment).data,
            }, status=200)


        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Ongoing appointment not found'}, status=400)
        except Specializations.DoesNotExist:
            return Response({'error': 'Specialization not found'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)




    













from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from analysis.models import *
from .models import *
from customer.models import *
from .serializers import (
    AppointmentDetailSerializer, PatientSerializer, GroupedQuestionAnswerSerializer,
    ExtraQuestionAnswerSerializer, ReferralSerializer, SuggestedPlanSerializer
)
from django.shortcuts import get_object_or_404

class AppointmentFullDetailsView(APIView):
    def get(self, request, appointment_id):
        appointment = get_object_or_404(AppointmentHeader, appointment_id=appointment_id)
        customer = appointment.customer

        appointment_data = AppointmentDetailSerializer(appointment).data
        patient_data = PatientSerializer(customer).data

        questionnaire_answers = AppointmentQuestionsAndAnswers.objects.filter(customer=appointment.customer)
        grouped = defaultdict(list)
        customer = appointment.customer

        # Preload all answers for the customer into a dict
        answers = {
            ans.question_id: ans.answer
            for ans in Extra_questions_answers.objects.filter(customer=customer)
        }

        extra_questions = [
            {
                "question": q.question,
                "question_id":q.id,
                "answer": answers.get(q.id)  # Will be None if no answer
            }
            for q in Extra_questions.objects.all()
        ]


        suggested_plans = Doctor_Suggested_Plans.objects.filter(refferral=appointment.referral)
        notes = Observation_Notes.objects.filter(appointment__customer = customer )
        response = {
            "appointment": appointment_data,
            "patient": patient_data,
            "questionnaire_answers": GroupedQuestionAnswerSerializer.from_queryset(questionnaire_answers),
            "extra_questions": extra_questions, 
            "referral": ReferralSerializer(appointment.referral).data if appointment.referral else None,
            "suggested_plans": SuggestedPlanSerializer(suggested_plans, many=True).data,
            "notes":Observation_notes_serializer(notes,many = True).data
        }

        return Response(response, status=status.HTTP_200_OK)




        # INSERT_YOUR_CODE

class AppointmentRescheduleView_Doctor(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        API to reschedule an appointment.
        Expects:
            - appointment_id: ID of the appointment to reschedule
        """
        data = request.data
        appointment_id = data.get('appointment_id')
     
     
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        if appointment.status in ['completed', 'cancelled']:
            return Response({"error": "Cannot reschedule a completed or cancelled appointment."}, status=status.HTTP_400_BAD_REQUEST)

     
        # Update appointment details
        appointment.status = 'rescheduled_by_doctor'
        appointment.meeting_link = ''
        appointment.start_time = None
        appointment.end_time = None
        appointment.appointment_date = None
        appointment.save()

      
        return Response({
            "message": "Appointment reschedule initiated.",
            "appointment_id": appointment.appointment_id
        }, status=status.HTTP_200_OK)








class PrescribedMedicationsCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')

        if not appointment_id :
            return Response({'error': 'appointment and medicine_details are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = DoctorProfiles.objects.get(user = request.user)
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except DoctorProfiles.DoesNotExist:
            return Response({'error': 'Doctor invalid not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['customer'] = appointment.customer.id
        data['doctor'] = doctor.doctor_profile_id

        serializer = PrescribedMedicationsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Medication added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrescribedTestsCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')

        if not appointment_id :
            return Response({'error': 'appointment and medicine_details are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = DoctorProfiles.objects.get(user = request.user)
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except DoctorProfiles.DoesNotExist:
            return Response({'error': 'Doctor invalid not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        customer = appointment.customer.id
        doctor = doctor.doctor_profile_id
        tests=request.data.get('tests')

        for test in tests:
            data = {'customer':customer,'doctor':doctor,'test_name':test.get('test_name'),'instruction':test.get('instruction'),'appointment':appointment}  
            serializer = PrescribedTestsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Tests Added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)




class AddObservatioinNotesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')
        note = request.data.get('note')

        if not appointment_id or not note:
            return Response({'error': 'appointment and note are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
       
        data = Observation_Notes.objects.create(appointment = appointment , note = note)


        return Response({'message': 'Note Added successfully'}, status=status.HTTP_201_CREATED)




class AddFollowUpNotesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')
        note = request.data.get('note')

        if not appointment_id or not note:
            return Response({'error': 'appointment and note are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
       
        data = Follow_Up_Notes.objects.create(appointment = appointment , note = note)


        return Response({'message': 'Note Added successfully'}, status=status.HTTP_201_CREATED)


