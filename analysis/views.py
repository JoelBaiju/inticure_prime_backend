from django.shortcuts import render
from rest_framework import generics
from django.shortcuts import render
from rest_framework import generics
from .models import *
from django.contrib.auth.models import User
from general.models import *
from general.utils import *
from general.twilio import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from customer.models import *
from doctor.models import *

# ======================FIRST ANALYSIS INTERROGATION ========================//




# ========API : 1=========verifying the user authenticity using email or phone along with existing user checking ========================//
# ========URL : /analysis/phone_email_submission/ ========================//

class PhoneNumberOrEmailSubmissionView(APIView):
    def get_serializer_class(self):
        return None
    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        country_code = request.data.get('country_code', '+91')  

        if phone_number:
            otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = generate_random_otp())
            send_otp_sms(otp = otp_instance.otp , to_number=country_code+phone_number)
            # send_otp_sms(otp = generate_random_otp() , to_number="+917034761676")
            print("OTP sent to phone number:", phone_number)
            
        if email:
            otp_instance = Email_OTPs.objects.create(email=email, otp=generate_random_otp())
            send_otp_email(otp = otp_instance.otp , toemail=email , firstname = ' user')
            # send_otp_email(otp = generate_random_otp() , toemail=email)
        
            
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'email': email
        }) 


# ========API : 2===========/analysis/phone_email_verification/ ========================//
    














from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class PhoneNumberOrEmailVerificationView(APIView):
    def get_serializer_class(self):
        return None

    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not otp or (not phone_number and not email):
            return Response({'error': 'Phone number or email and OTP are required.'}, status=HTTP_400_BAD_REQUEST)

        user = None

        # Phone OTP verification
        if phone_number:
            try:
                phone_otp = Phone_OTPs.objects.get(phone=phone_number, otp=otp)
                user = User.objects.filter(username=phone_number).first()
            except Phone_OTPs.DoesNotExist:
                return Response({'error': 'Invalid OTP for phone number', 'verified': False}, status=HTTP_400_BAD_REQUEST)

        # Email OTP verification
        if email:
            try:
                email_otp = Email_OTPs.objects.get(email=email, otp=otp)
                user = User.objects.filter(email=email).first()
            except Email_OTPs.DoesNotExist:
                return Response({'error': 'Invalid OTP for email', 'verified': False}, status=HTTP_400_BAD_REQUEST)

        if user:
            # Existing user
            refresh = RefreshToken.for_user(user)
            return Response({
                'user_exists': True,
                'verified': True,
                'message': 'Existing user Verified',
                'user_id': user.id,
                'sessionid': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=HTTP_200_OK)
        else:
            # Create new user
            username = phone_number or email
            if not username:
                return Response({'error': 'Username could not be determined.'}, status=HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                username=username,
                email=email if email else None,
                password=otp  # optional: generate a random password instead
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                'user_exists': False,
                'verified': True,
                'message': 'New user created and verified',
                'user_id': user.id,
                'sessionid': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=HTTP_200_OK)





# ========API : 3=========Adding the gender and category of the user for new users and send the questionnaire data based on the gender and cat ========================//
# ========URL : ==========/analysis/submit_gender_category/ ========================//


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from customer.models import CustomerProfile
from .models import Category, Questionnaire, Options
from .serializers import *

class SubmitGenderCategoryView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # This method can be used to retrieve categories if needed
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True).data
        return Response({
            'response_code': 200,
            'status': 'Ok',
            'data': serialized_categories
        })

    def post(self, request):
        if user.is_anonymous:
            return Response({'error': 'User is not authenticated'}, status=HTTP_401_UNAUTHORIZED)
        user = request.user
        category_id = request.data.get('category')
        gender = request.data.get('gender')

        if not gender:
            return Response({'error': 'Gender is required'}, status=HTTP_400_BAD_REQUEST)

        category_instance = None
        if category_id:
            try:
                category_instance = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({'error': 'Category does not exist'}, status=HTTP_400_BAD_REQUEST)

    
        if not CustomerProfile.objects.filter(user=user).exists():
            CustomerProfile.objects.create(
                user=user,
                gender=gender,
            )

            appointment=AppointmentHeader.objects.create(
                user=user,
                category=category_instance)
                


        try:
            filter = {}
            filter['category_id'] = category_id
            filter['customer_gender'] = gender

            questionnaire_serialized = QuestionnaireSerializer(Questionnaire.objects.filter(**filter), many=True).data
            
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)

        for question in questionnaire_serialized:
            try:
                question['options'] = OptionsSerializer(Options.objects.filter(question=question),
                                                        many=True).data
            except:
                question['options'] = ""
        return Response({
            'response_code': 200,
            'status': 'Ok',
            'data': questionnaire_serialized
        })
       
        return Response({'message': 'Profile created successfully'}, status=HTTP_200_OK)






# ========API : 4========= Saving the selected answers from question ========================//
# ========URL : ==========/analysis/submit_questionnaire/ ========================//


class SubmitQuestionnaireView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        answers = request.data.get('answers', [])

        if not answers:
            return Response({'error': 'Answers are required'}, status=HTTP_400_BAD_REQUEST)

        for answer in answers:
            question = answer.get('question')
            answer = answer.get('option')

            if not question or not answer:
                return Response({'error': 'Question ID and selected option are required'}, status=HTTP_400_BAD_REQUEST)

            # Save the answer (you may need to create a model for this)
            AppointmentQuestions.objects.create(
                appointment_id=AppointmentHeader.objects.get(user=user),
                question=Questionnaire.objects.get(id=question),
                answer=Options.objects.get(id=answer),
                user=user
            )

        return Response({'message': 'Answers submitted successfully'}, status=HTTP_200_OK)









# ========API : 5=========GET: submitting preferences and getting the available slots   ========================//
# ========URL : ==========/analysis/get_available_slots/ ========================//

from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

class SlotsBooking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        preffered_gender = request.query_params.get('preferred_gender')
        preffered_language = request.query_params.get('preferred_language')
        print(preffered_gender, preffered_language)
        
        # Get tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_date = tomorrow.date()

        # Base query for available slots tomorrow
        base_query = Q(is_available=True) & Q(date__date=tomorrow_date)

        # Case 1: Both preferences provided
        if preffered_gender and preffered_language:
            appointment = AppointmentHeader.objects.filter(user=user).first()
            appointment.language_pref = preffered_language
            appointment.gender_pref = preffered_gender
            appointment.save()
            # Filter doctors by gender and language
            preferred_doctors = DoctorProfiles.objects.filter(
                gender=preffered_gender,
                doctorlanguages__language__language__iexact=preffered_language
            ).distinct()

            # Filter available slots for preferred doctors tomorrow
            preferred_slots = DoctorAvailableSlots.objects.filter(
                base_query,
                doctor__in=preferred_doctors
            ).select_related('doctor', 'date', 'time_slot')

            if preferred_slots.exists():
                data = self._serialize_slots(preferred_slots)
                return Response({
                    "message": "Slots matching your preferences",
                    "available_slots": data,
                    "matched_preferences": True
                }, status=200)

        # Case 2: Either no preferences or no slots matched preferences - return all available tomorrow
        all_slots_tomorrow = DoctorAvailableSlots.objects.filter(
            base_query
        ).select_related('doctor', 'date', 'time_slot')

        data = self._serialize_slots(all_slots_tomorrow)
        
        response_data = {
            "available_slots": data,
            "matched_preferences": False if (preffered_gender and preffered_language) else None
        }
        
        if preffered_gender and preffered_language:
            response_data["message"] = "No slots matching preferences, showing all available slots"

        return Response(response_data, status=200)

    def _serialize_slots(self, slots):
        """Helper method to serialize slot data"""
        return [
            {
                "doctor_id": slot.doctor.doctor_profile_id,
                "doctor": slot.doctor.user.get_full_name(),
                "doctor_gender": slot.doctor.gender,
                "doctor_languages": list(slot.doctor.doctorlanguages_set.all().values_list('language__language', flat=True)),
                "date": slot.date.date,
                "day": slot.date.day,
                "from_time": slot.time_slot.from_time,
                "to_time": slot.time_slot.to_time,
                "slot_id": slot.id
            }
            for slot in slots
        ]







# ========API : 6========= submitting personal data along with the selected slot language selected  ========================//
# ========URL : ==========/analysis/submit_personal_data/ ========================//


from customer.serializers import CustomerProfileSerializer
from rest_framework.generics import CreateAPIView
from rest_framework import status

class FinalSubmit(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def post(self, request):
        user = request.user

        if CustomerProfile.objects.filter(user=user).exists():
            return Response({"error": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['user'] = user.id  # Add user ID to the data manually
        slot_id = data.pop('slot_id', None)  # Remove user_id if it exists in the data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # return Response({"message": "Profile submitted successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return allotDoctor(user,slot_id)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def allotDoctor(user,slot_id):
    try:
        appointment = ApointmentHeader.objects.filter(user=user).first()
        slot = DoctorAvailableSlots.objects.filter(id=slot_id).first()
    except ApointmentHeader.DoesNotExist:
        return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
    except DoctorAvailableSlots.DoesNotExist:
        return Response({"error": "Slot not found."}, status=status.HTTP_404_NOT_FOUND)
   


    if slot.is_available == False:
        return Response({"error": "Slot is not available."}, status=status.HTTP_400_BAD_REQUEST)
        
    slot.is_available = False
    slot.save()


    if appointment:
        preffered_gender = appointment.gender_pref
        preffered_language = appointment.language_pref



def calculateTotalFee(doctor):
    doctor_fee = doctor.doctor_payment_rate.rate_per_session



    


