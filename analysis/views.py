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
from inticure_prime_backend.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER

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
        print(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER)
        print("Phone number:", phone_number)
        if phone_number:
            print("Phone number received and got in:", phone_number)
            otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = generate_random_otp())
            send_otp_sms(otp = otp_instance.otp , to_number=country_code+phone_number)
            # send_otp_sms(otp = generate_random_otp() , to_number="+917034761676")
            print("OTP sent to phone number:", phone_number)
            
        if email:
            otp_instance = Email_OTPs.objects.create(email=email, otp=generate_random_otp())
            send_otp_email(otp = otp_instance.otp , toemail=email , firstname = ' user')
            print("OTP sent to email:", email)
            # send_otp_email(otp = generate_random_otp() , toemail=email)
        
            
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'email': email
        }) 


# ========API : 2===========/analysis/phone_email_verification/ ========================//
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
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
            try :
                customer_profile = CustomerProfile.objects.get(user=user)
                if customer_profile.completed_first_analysis:
                    exists = True
                else:
                    exists = False

            except CustomerProfile.DoesNotExist:
                exists = False

            
            # Existing user
            refresh = RefreshToken.for_user(user)
            return Response({
                'user_exists': exists,
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
                password=otp
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
    permission_classes = [IsAuthenticated]

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
        user = request.user
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
            customer_profile = CustomerProfile.objects.create(
                user=user,
                gender=gender,
            )

        else :
            customer_profile = CustomerProfile.objects.get(user=user)

        appointment=AppointmentHeader.objects.create(
            customer=customer_profile,
            category=category_instance,
            appointment_status=1,  # Assuming 1 means 'pending' or 'new'
            )
                


        try:
            filter = {}
            filter['category_id'] = category_id
            filter['customer_gender'] = gender

            questionnaire_serialized = QuestionnaireSerializer(Questionnaire.objects.filter(**filter), many=True).data
            
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)

        for question in questionnaire_serialized:
            try:
                question['options'] = OptionsSerializer(Options.objects.filter(question=question['id']),  
                                                        many=True).data
            except Exception as e:
                print("Error fetching options for question:", question['id'], e)
                question['options'] = ""
        return Response({
            'response_code': 200,
            'status': 'Ok',
            'questionnaire': questionnaire_serialized
        })
       
        return Response({'message': 'Profile created successfully'}, status=HTTP_200_OK)






# ========API : 4========= Saving the selected answers from question ========================//
# ========URL : ==========/analysis/submit_questionnaire/ ========================//


class SubmitQuestionnaireView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        answers = request.data.get('answers', [])
        try:
            customer = CustomerProfile.objects.get(user=user)
        
        except :
            return  Response({'error': 'Seems like you missed something ,Please start again'}, status=HTTP_400_BAD_REQUEST)
        if not answers:
            return Response({'error': 'Answers are required'}, status=HTTP_400_BAD_REQUEST)

        for answer in answers:
            question = answer.get('question')
            options = answer.get('option')

            if not question or not options:
                return Response({'error': 'Question ID and selected option are required'}, status=HTTP_400_BAD_REQUEST)

            # Save the answer (you may need to create a model for this)
            for option in options:

                AppointmentQuestionsAndAnswers.objects.create(
                    appointment = AppointmentHeader.objects.get(customer=customer),
                    question=Questionnaire.objects.get(id=question),
                    answer=Options.objects.get(id=option),
                    customer= customer
                )
        appointment = AppointmentHeader.objects.get(customer=customer)
        appointment.appointment_status = 2
        appointment.save()

        return Response({'message': 'Answers submitted successfully'}, status=HTTP_200_OK)









# ========API : 5=========GET: for getting available languages  ========================//
# ========URL : ==========/analysis/get_available_languages/ ========================//

from doctor.serializers import DoctorLanguagesSerializer

class GetAvailableLanguages(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Pull only the unique language names from related model
        unique_languages = (
            DoctorLanguages.objects
            .values('language__language')  # or .values('language__name') depending on your field
            .distinct()
        )

        # Restructure result to a clean format
        languages_list = [{'language': item['language__language']} for item in unique_languages]

        return Response({
            'response_code': 200,
            'status': 'Ok',
            'languages': languages_list
        })

# ========API : 6=========GET: submitting preferences and getting the available slots   ========================//
# ========URL : ==========/analysis/get_available_slots/ ========================//


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import datetime, timedelta
from django.db.models import Q
from django.core.cache import cache
from general.models import UserPreferredDoctors

class SlotsBooking(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Extract preference data from request body
        gender_info = request.data.get('preferred_gender', {})
        language_info = request.data.get('preferred_language', {})
        preferred_date = request.data.get('preferred_date')

        gender = gender_info.get('value')
        gender_priority = int(gender_info.get('priority', 0)) if gender_info else 0

        language = language_info.get('value')
        language_priority = int(language_info.get('priority', 0)) if language_info else 0

        # Start date from preferred or tomorrow
        base_date = datetime.now().date() + timedelta(days=1)
        if preferred_date:
            try:
                base_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Save preferences to AppointmentHeader
        appointment = AppointmentHeader.objects.filter(customer=CustomerProfile.objects.get(user=user)).first()
        
        if appointment:
            if gender: appointment.gender_pref = gender
            if language: appointment.language_pref = language
            appointment.save()

        doctors = DoctorProfiles.objects.filter(doctor_flag="junior")
        q_gender = Q(gender=gender) if gender else Q()
        q_language = Q(doctorlanguages__language__language__iexact=language) if language else Q()

        preferred_doctors = DoctorProfiles.objects.none()

        gender_matched = False
        language_matched = False

        if gender and language :
            preferred_doctors = doctors.filter(q_gender & q_language).distinct()
    
            if not preferred_doctors.exists():
                print("No doctors matched both preferences, checking individually")
                if  gender_priority > language_priority:
                    preferred_doctors = doctors.filter(q_gender).distinct()
                    if preferred_doctors.exists():
                        gender_matched = True
                elif language_priority > gender_priority:
                    preferred_doctors = doctors.filter(q_language).distinct()
                    if preferred_doctors.exists():
                        language_matched = True

                if not preferred_doctors.exists():
                    print("No doctors matched single high priority preference, checking fallback ")
                    if gender_priority > language_priority:
                        preferred_doctors = doctors.filter(q_language).distinct()
                        if preferred_doctors.exists():
                            language_matched = True

                    elif language_priority > gender_priority:
                        preferred_doctors = doctors.filter(q_gender).distinct()
                        if preferred_doctors.exists():
                           gender_matched = True

                if preferred_doctors.exists():
                    print(preferred_doctors)
                    print("Fallback to one preference match")
            
            else:
                gender_matched = True
                language_matched = True

        print(preferred_doctors)
        print(gender_matched, "gender matched")
        print(language_matched, "language matched")
        
        preferred_doctor_ids = list(preferred_doctors.values_list('doctor_profile_id', flat=True))



        print("Preferred doctor IDs:", preferred_doctor_ids)
        user_preferred_doctors, created = UserPreferredDoctors.objects.get_or_create(user_id=user.id)
        if created:
            for doctor_id in preferred_doctor_ids:
                user_preferred_doctors.add_doctor(doctor_id)
        else:
            user_preferred_doctors.clear_doctors()
            for doctor_id in preferred_doctor_ids:
                user_preferred_doctors.add_doctor(doctor_id)
        user_preferred_doctors.save()

        # Find available slots for the next 14 days (safe cap)
        max_days = 14
        current_date = base_date
        matched_slots = None
        matched_date = None
        all_available_dates = []

        for i in range(max_days):
            # All doctors available on this date
            slots_today = GeneralTimeSlots.objects.filter(
                doctor_availability__doctor__in=preferred_doctors,
                doctor_availability__is_available=True,
                doctor_availability__date__date=current_date
            ).select_related('date').distinct()

            if slots_today.exists() and matched_slots is None:
                matched_slots = slots_today
                matched_date = current_date

            if slots_today.exists():
                all_available_dates.append(str(current_date))

            current_date += timedelta(days=1)

        # If matched slots found
        if matched_slots:
            return Response({
                "message": f"Slots matching preferences found on {matched_date}",
                "available_slots": self._serialize_slots(matched_slots),
                "matched_preferences": True,
                "gender_matched":gender_matched,
                "language_matched": language_matched,
                "available_dates": all_available_dates
            }, status=200)

        # No match with preferences; fallback to all doctors (any slot)
        fallback_current_date = base_date
        fallback_slots = None
        fallback_dates = []

        for i in range(max_days):
            all_slots = GeneralTimeSlots.objects.filter(
                doctor_availability__is_available=True,
                doctor_availability__date__date=fallback_current_date
            ).select_related('date').distinct()

            if all_slots.exists() and fallback_slots is None:
                fallback_slots = all_slots

            if all_slots.exists():
                fallback_dates.append(str(fallback_current_date))

            fallback_current_date += timedelta(days=1)

        return Response({
            "message": "No slots matching preferences, showing all available slots",
            "available_slots": self._serialize_slots(fallback_slots) if fallback_slots else [],
            "matched_preferences": False,
            "gender_matched":gender_matched,
            "language_matched": language_matched,
            "available_dates": fallback_dates,
            'fallback_message': "Showing all available slots for the next 14 days.",
        }, status=200)

    def _serialize_slots(self, slots):
        return [
            {
                "date": slot.date.date,
                "day": slot.date.day,
                "time": f"{slot.from_time.strftime('%H:%M')} - {slot.to_time.strftime('%H:%M')}",
                "slot_id": slot.id
            }
            for slot in slots
        ]






# ========API : 7========= submitting personal data along with the selected slot language selected  ========================//
# ========URL : ==========/analysis/submit_personal_data/ ========================//


from customer.serializers import CustomerProfileSerializer
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

class FinalSubmit(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def post(self, request):
        user = request.user
        try:
            # Extract form data
            dob = request.data.get('dob')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            message = request.data.get('message')
            preferred_name = request.data.get('preferred_name')
            slot_id = request.data.get('slot_id')
            
            confirmation_method = request.data.get('confirmation_method')
            phone_number = request.data.get('phone_number')
            email = request.data.get('email')
            country_code = request.data.get('country_code', '+91')  


            # Validate confirmation method
            if confirmation_method not in ["SMS", "Email", "WhatsApp"]:
                return Response({'error': 'Invalid confirmation method'}, status=status.HTTP_400_BAD_REQUEST)
            if confirmation_method in ["SMS", "WhatsApp"] and not request.data.get('phone_number'):
                return Response({'error': 'Phone number is required for SMS/WhatsApp'}, status=status.HTTP_400_BAD_REQUEST)
            if confirmation_method == "Email" and not request.data.get('email'):
                return Response({'error': 'Email is required for Email confirmation'}, status=status.HTTP_400_BAD_REQUEST)

            # Update customer profile
            customerProfile, created = CustomerProfile.objects.get_or_create(user=user)
            customerProfile.date_of_birth = dob
            customerProfile.preferred_name = preferred_name
            customerProfile.save()

            # Update user's name
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Update appointment message
            appointment = AppointmentHeader.objects.filter(customer=customerProfile).first()
            if appointment:
                appointment.customer_message = message
                appointment.appointment_status = 3 
                appointment.confirmation_method = confirmation_method
                appointment.confirmation_phone_number = phone_number if confirmation_method in ["SMS", "WhatsApp"] else None
                appointment.confirmation_email = email if confirmation_method == "Email" else None
                appointment.save()

            # Allot doctor based on preferred doctors and slot
            return AllotDoctor(request.user.id, customerProfile,slot_id)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def AllotDoctor(user_id,customer, slot_id):
    try:
        appointment = AppointmentHeader.objects.get(customer=customer)
        slot = GeneralTimeSlots.objects.get(id=slot_id)
    except AppointmentHeader.DoesNotExist:
        return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
    except GeneralTimeSlots.DoesNotExist:
        return Response({"error": "Slot not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get preferred doctors from cache

    preferred_doctors = UserPreferredDoctors.objects.filter(user_id=user_id).first()
    if preferred_doctors:  
        preferred_doctors = preferred_doctors.get_doctor_ids()
    else:   
        return Response({"error": "Preferred doctors not found in cache."}, status=status.HTTP_404_NOT_FOUND)
        
    print("Preferred doctors from cache:", preferred_doctors)   
    print(slot_id )



    if not preferred_doctors:
        return Response({"error": "Preferred doctors not available in cache."}, status=status.HTTP_400_BAD_REQUEST)

    # Find available doctor for the given slot
    available_doctor_slot = DoctorAvailableSlots.objects.filter(
        doctor__doctor_profile_id__in=preferred_doctors,
        is_available=True,
        time_slot=slot
    ).select_related('doctor').first()

    if not available_doctor_slot:
        return Response({"error": "No preferred doctor available for this slot."}, status=status.HTTP_404_NOT_FOUND)

    # Assign doctor to appointment and update availability
    appointment.doctor = available_doctor_slot.doctor
    appointment.appointment_status = 4
    appointment.save()

    # Mark doctor slot and general slot as unavailable
    available_doctor_slot.is_available = False
    available_doctor_slot.save()

    from general.smss import appointmentbooked

    if appointment.confirmation_method == "SMS":
        appointmentbooked(appointment)
    return Response({
        "message": "Appointment confirmed and doctor assigned.",
        "assigned_doctor_id": available_doctor_slot.doctor.doctor_profile_id,
        "slot_id": slot.id
    }, status=status.HTTP_200_OK)




