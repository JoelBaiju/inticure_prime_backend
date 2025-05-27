from django.shortcuts import render
from rest_framework import generics
from .models import *
from django.contrib.auth.models import User
from general.models import *
from general.utils import *
from general.twilio import *
from rest_framework.response import Response
from rest_framework.views import APIView




class PhoneNumberOrEmailSubmissionView(APIView):
    def get_serializer_class(self):
        return None
    def post(self, request):
        print(request.data["phone_number"])
        # Handle the form submission for phone number or email
        phone_number = request.data.get('phone_number')
        email = request.POST.get('email')
        
        if phone_number:
            # otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = generate_random_otp())
            # send_otp_sms(otp = otp_instance.otp , to_number=phone_number)
            send_otp_sms(otp = generate_random_otp() , to_number=phone_number)
            print("OTP sent to phone number:", phone_number)
        if email:
            # otp_instance = Email_OTPs.objects.create(email=email, otp=generate_random_otp())
            # send_otp_email(otp = otp_instance.otp , toemail=email)
            send_otp_email(otp = generate_random_otp() , toemail=email)
        
            
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'email': email
        }) 
    



