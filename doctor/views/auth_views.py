from functools import total_ordering
from pydoc import doc
from tracemalloc import start
from razorpay.resources import customer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from twilio.rest import api
from administrator.models import LanguagesKnown,Countries , Specializations
from administrator.serializers import LanguagesKnownSerializer, CountriesSerializer ,SpecializationsSerializer
from general.emal_service import send_payment_pending_email
from inticure_prime_backend.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from general.models import Phone_OTPs , Email_OTPs
from general.utils import send_otp_email 
from general.twilio import send_otp_sms
from general.utils import generate_random_otp
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from django.core.exceptions import MultipleObjectsReturned



from general.whatsapp.whatsapp_messages import send_wa_auth_code

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(APIView):
    def get_serializer_class(self):
        return None
    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email_id')
        country_code = request.data.get('country_code', '+91')  

        otp = generate_random_otp()
        # otp = 666666

        if phone_number:
            if not DoctorProfiles.objects.filter(whatsapp_number = phone_number).exists():
                return Response('The provided mobile number is not connected with any account',status=status.HTTP_400_BAD_REQUEST)

            print("Phone number received and got in:", phone_number)


               
            try:
                otp_instance, created = Phone_OTPs.objects.get_or_create(phone=phone_number)
                otp_instance.otp = otp
                otp_instance.save()
            except MultipleObjectsReturned:
                Phone_OTPs.objects.filter(phone=phone_number).delete()
                otp_instance = Phone_OTPs.objects.create(phone=phone_number, otp=otp)
       
            # send_otp_sms(otp = otp_instance.otp , to_number=country_code+phone_number)
            send_wa_auth_code(str(country_code) + str(phone_number) ,otp)
            print("OTP sent to phone number:", phone_number)
            
        if email:
            if not DoctorProfiles.objects.filter(email_id = email).exists():
                return Response('The provided email id is not connected with any account',status=status.HTTP_400_BAD_REQUEST)


            try:
                otp_instance, created = Email_OTPs.objects.get_or_create(email=email)
                otp_instance.otp = otp
                otp_instance.save()
            except MultipleObjectsReturned:
                Email_OTPs.objects.filter(email=email).delete()
                otp_instance = Email_OTPs.objects.create(email=email, otp=otp)
            
            send_otp_email(otp = otp_instance.otp , toemail=email , firstname = 'user')
            print("OTP sent to email:", email)
        
            print(otp_instance.otp)

        
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'email': email
        }) 






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

                doctor_profile = DoctorProfiles.objects.get(whatsapp_number=phone_number)
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
                password=otp,
                is_staff = True
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
from ..models import DoctorSpecializations,DoctorProfiles
from ..serializers import *

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_doctor_profile(request):
    # Handle specializations[] manually
    specialization_ids = request.data.getlist('specializations[]')
    language_ids       = request.data.getlist('language_ids[]')
    salutation        = request.data.get('salutation')
    print(salutation)
    # Copy other data to mutable form
    data = request.data

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





