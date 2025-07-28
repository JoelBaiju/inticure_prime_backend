from django.forms import ValidationError
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


# analysis/views.py
class StartAnalysisView(APIView):
    def get(self, request):
        session = AnalysisSession.objects.create()
        return Response({
            "message": "Analysis session started",
            "analysis_token": str(session.token)
        }, status=200)
    

def get_analysis_session(token):
    try:
        return AnalysisSession.objects.get(token=token)
    except AnalysisSession.DoesNotExist:
        raise ValidationError("Invalid or expired analysis token.")


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
            otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = '666666')
            # otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = generate_random_otp())
            # send_otp_sms(otp = otp_instance.otp , to_number=country_code+phone_number)
            print("OTP sent to phone number:", phone_number)
            
        if email:
            otp_instance = Email_OTPs.objects.create(email=email, otp='666666')
            # otp_instance = Email_OTPs.objects.create(email=email, otp=generate_random_otp())
            send_otp_email(otp = otp_instance.otp , toemail=email , firstname = ' user')
            print("OTP sent to email:", email)
        
            
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

        if phone_number:
            try:
                phone_otp = Phone_OTPs.objects.filter(phone=phone_number, otp=otp).order_by('-created_at').first()
                if not phone_otp:
                    return Response('Invalid OTP for phone number', status=HTTP_400_BAD_REQUEST)

                user = User.objects.filter(username=phone_number).first()

            except DoctorProfiles.DoesNotExist:
                return Response('Account not found, Invalid phone number', status=HTTP_400_BAD_REQUEST)

        # Email OTP verification
        if email:
            try:
                email_otp = Email_OTPs.objects.filter(email=email, otp=otp).order_by('-created_at').first()
                if not email_otp:
                    return Response('Invalid OTP for email', status=HTTP_400_BAD_REQUEST)

                user = User.objects.filter(email=email).first()

            except DoctorProfiles.DoesNotExist:
                return Response('Account not found, Invalid Email ID', status=HTTP_400_BAD_REQUEST)
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
            customer_profile = CustomerProfile.objects.create(
                user=user,
                mobile_number=phone_number if phone_number else None,
                completed_first_analysis=False,
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
        token = request.data.get("analysis_token")
        if not token:
            return Response({'error': 'Missing analysis_token'}, status=400)

        try:
            session = AnalysisSession.objects.get(token=token)
        except AnalysisSession.DoesNotExist:
            return Response({'error': 'Invalid analysis_token'}, status=400)

        gender = request.data.get('gender')
        category_id = request.data.get('category')

        if not gender:
            return Response({'error': 'Gender is required'}, status=400)

        # Save gender
        session.gender = gender

        # Save category if provided
        if category_id:
            try:
                category_instance = Category.objects.get(id=category_id)
                session.category = category_instance
            except Category.DoesNotExist:
                return Response({'error': 'Category does not exist'}, status=400)

        session.save()
        print(category_id,gender)
        # Now fetch questionnaire based on gender (and optionally category)
        filter = {}
        # Use the correct field name as per your Questionnaire model
        # For example, if the field is 'gender' and 'category', use those
        filter_field_gender = 'customer_gender'  # Change this to your actual field name in Questionnaire
        filter_field_category = 'category'  # Change this to your actual field name in Questionnaire

        filter[filter_field_gender] = gender
        if session.category:
            filter[filter_field_category] = session.category

        try:
            questionnaire = Questionnaire.objects.filter(customer_gender = gender )
            print("Questionnaire:", questionnaire)
            questionnaire_serialized = QuestionnaireSerializer(questionnaire, many=True).data

            for question in questionnaire_serialized:
                question['options'] = OptionsSerializer(
                    Options.objects.filter(question=question['id']),
                    many=True
                ).data
        except Category.DoesNotExist:
            return Response({'error': 'Category does not exist'}, status=400)
        except ValidationError as ve:
            return Response({'error': str(ve)}, status=400)
        print("Questionnaire data:", questionnaire_serialized)
        return Response({
            'response_code': 200,
            'status': 'Ok',
            'questionnaire': questionnaire_serialized
        })





# ========API : 4========= Saving the selected answers from question ========================//
# ========URL : ==========/analysis/submit_questionnaire/ ========================//
class SubmitQuestionnaireView(APIView):
    def post(self, request):
        token = request.data.get("analysis_token")
        answers = request.data.get("answers", [])

        if not token:
            return Response({"error": "Missing analysis_token"}, status=400)
        if not answers:
            return Response({"error": "Answers are required"}, status=400)

        try:
            session = AnalysisSession.objects.get(token=token)
        except AnalysisSession.DoesNotExist:
            return Response({"error": "Invalid analysis_token"}, status=400)

        for answer in answers:
            question_id = answer.get("question")
            option_ids = answer.get("option", [])

            if not question_id or not option_ids:
                return Response({"error": "Question ID and selected option are required"}, status=400)

            for option_id in option_ids:
                AppointmentQuestionsAndAnswers.objects.create(
                    tempsession=session,
                    question_id=question_id,
                    answer_id=option_id
                )

        session.analysis_status = "questionnaire_completed"
        session.save()

        return Response({"message": "Answers saved successfully"}, status=200)







# ========API : 5=========GET: for getting available languages  ========================//
# ========URL : ==========/analysis/get_available_languages/ ========================//

from doctor.serializers import DoctorLanguagesSerializer

class GetAvailableLanguages(APIView):

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
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from doctor.slots_service import get_available_slots





class SlotsBooking(APIView):
    def post(self, request):
        token = request.data.get("analysis_token")
        gender_info = request.data.get('preferred_gender', {})
        language_info = request.data.get('preferred_language', {})
        preferred_date = request.data.get('preferred_date')
        country = request.data.get('country')
        specialization_id = request.data.get('specialization')  # Ensure it's an ID
        is_couple = request.data.get('is_couple', False)
        is_junior = request.data.get('is_junior', False)
        alignment_minutes = request.data.get('alignment_minutes')  # Optional
        specialization = request.data.get('specialization_name', "No Specialization")  
        authorization = request.headers.get('Authorization')
        first_analysis = request.data.get('first_analysis', False)

        if first_analysis:
            if not token:
                return Response({"error": "Missing analysis_token"}, status=400)

            try:
                session = AnalysisSession.objects.get(token=token)
            except AnalysisSession.DoesNotExist:
                return Response({"error": "Invalid analysis_token"}, status=400)


            # Save preferences in session
            session.gender_preference = gender_info.get("value")
            session.language_preference = language_info.get("value")
            session.preferred_date = preferred_date
            session.specialization_id = specialization_id
            session.specialization_name = specialization
            session.country = country
            session.is_couple = is_couple
            session.is_junior = is_junior
            session.alignment_minutes = alignment_minutes
            session.analysis_status = "slots_queried"
            session.save()


        try:
            base_date = datetime.now().date() + timedelta(days=1)
            print(datetime.now())
            print(base_date)
            preferred_date = datetime.strptime(preferred_date, '%Y-%m-%d').date() if preferred_date else base_date
            print(preferred_date)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if not specialization_id or  specialization_id == "No Specialization":
            print('no Specialization')
            specialization_id = Specializations.objects.filter(specialization = "No Specialization").specialization_id
        
        slot_data = get_available_slots(
            specialization_id=specialization_id,
            date=preferred_date,
            is_couple=is_couple,
            alignment_minutes=alignment_minutes,
            is_junior=is_junior,
            gender_info=gender_info,
            language_info=language_info,
            country=country,
            specialization=specialization
        )

        return Response({   
            "slots": slot_data["slots"],
            "matched_preferences": slot_data["matched_preferences"],
            "gender_matched": slot_data["gender_matched"],
            "language_matched": slot_data["language_matched"],
            "available_dates": slot_data["available_dates"],
            "fallback_message": slot_data["fallback_reason"] or "",
            "doctors_found_but_unavailable": slot_data["doctors_found_but_unavailable"]
        }, status=200)



from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import DoctorProfiles
from .serializers import DoctorProfilePublicSerializer


@api_view(['POST'])
def get_multiple_doctor_profiles(request):
    doctor_ids = request.data.get("doctor_ids")
    country = request.data.get("country")
    specialization_id = request.data.get("specialization_id")
    is_couple = request.data.get("is_couple")
    try:
        specialization = Specializations.objects.get(specialization_id =specialization_id)
        print(specialization)
    except Specializations.DoesNotExist:
        return Response({'error': 'specialization invalid'}, status=400)
    if not doctor_ids or not isinstance(doctor_ids, list):
        return Response(
            {"detail": "doctor_ids must be a list of IDs."},
            status=status.HTTP_400_BAD_REQUEST
        )

    doctors = DoctorProfiles.objects.filter(pk__in=doctor_ids)
    if not doctors.exists():
        return Response({"detail": "No matching doctors found."}, status=404)

    serialized = DoctorProfilePublicSerializer(doctors, many=True)
    response_data = serialized.data  # list

    for doc in response_data:
        rule = DoctorPaymentRules.objects.filter(
            doctor__doctor_profile_id=doc['doctor_profile_id'],
            country__country_name=country,
            specialization = specialization
        ).first()
        if rule:
            if is_couple:
                doc['final_price'] = rule.get_effective_payment()['custom_user_total_fee_couple'] if rule else None
            else:
                print(rule.get_effective_payment)
                doc['final_price'] = rule.get_effective_payment()['custom_user_total_fee_single'] if rule else None
        
    try:
        country_obj = Countries.objects.get(country_name=country)
        currency = country_obj.currency
        currency_symbol = country_obj.currency_symbol
    except Countries.DoesNotExist:
        currency = None
        currency_symbol = None

    return Response({
        "country": country,
        "currency": currency,
        "currency_symbol": currency_symbol,
        "doctors": response_data
    }, status=200)




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
from general.gmeet.gmeet import generate_google_meet


from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework import status
from django.utils import timezone
from datetime import datetime
# from .models import CustomerProfile, AppointmentHeader, GeneralTimeSlots, DoctorAvailableSlots, Countries
from general.models import UserPreferredDoctors
from customer.serializers import CustomerProfileSerializer
from general.utils import calculate_age, calculate_from_to_time_with_date
from general.utils import send_appointment_confirmation_email
from general.smss import appointmentbooked


class FinalSubmit(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    def post(self, request):
        try:
            user = request.user
            data = request.data
            token = data.get('analysis_token')

            
          

            try:
                customer_profile    = CustomerProfile.objects.get(user=user)

                if not customer_profile.completed_first_analysis:
                    country             = Countries.objects.get(country_name=data.get('country'))
                    if not token:
                        return Response({'error': 'Missing analysis_token'}, status=400)
                    session             = AnalysisSession.objects.get(token=token)

                    customer_profile.gender         = session.gender
                    customer_profile.date_of_birth  = data.get('dob')
                    customer_profile.age            = calculate_age(data.get('dob'))
                    customer_profile.preferred_name  = data.get('preferred_name')
                    customer_profile.country_details = country
                    customer_profile.save()

                    user.first_name = data.get('first_name')
                    user.last_name = data.get('last_name')
                    user.save()

                    category        = session.category
                    gender_pref     = session.gender
                    language_pref   = session.language_preference
                    specialization  = session.specialization
                    is_couple       = session.is_couple
                    
                    answer_objs = AppointmentQuestionsAndAnswers.objects.filter(tempsession=session)
                    
                    for ans in answer_objs:
                        ans.customer = customer_profile
                        ans.save()

                    session.status = "final_submitted"
                    session.save()
                
                else :
                    category        = Category.objects.get(id= data.get('category'))
                    gender_pref     = data.get('gender_pref')
                    language_pref   = data.get('language_pref')

                    specialization  = Specializations.objects.get(specialization_id=data.get('specialization'))
                    is_couple               = True if data.get('is_couple')else False,                

            except CustomerProfile.DoesNotExist:
                return Response({'error': 'Customer profile not found'}, status=400)
            except Countries.DoesNotExist:
                print("country",data.get('country'))
                return Response({'error': 'Invalid country'}, status=400)
            except AnalysisSession.DoesNotExist:
                return Response({'error': 'Invalid analysis_token'}, status=400)


            # Update user details
         

            # Appointment slot
            slot = data.get('slot', {})
            slot_date = datetime.strptime(slot.get('date'), "%Y-%m-%d").date()
            from_time = datetime.strptime(slot.get('start'), "%H:%M:%S").time()
            to_time = datetime.strptime(slot.get('end'), "%H:%M:%S").time()
            doctor_id = data.get('doctor_id')
            doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)

            # Check slot overlap
            overlapping = DoctorAppointment.objects.filter(
                doctor=doctor,
                date__date=slot_date,
                start_time__lt=to_time,
                end_time__gt=from_time
            ).exists()
            if overlapping:
                return Response({'error': 'The selected time slot overlaps with an existing appointment.'}, status=409)

            # Create new appointment
            print(specialization)
            appointment = AppointmentHeader.objects.create(
                    customer                = customer_profile,
                    category                = category,
                    gender_pref             = gender_pref,
                    appointment_status      = "pending_payment",
                    status_detail           = "initiated by customer waiting for payment",
                    confirmation_method     = data.get('confirmation_method'),
                    confirmation_phone_number= data.get('phone_number') if data.get('confirmation_method') in ["SMS", "WhatsApp"] else None,
                    confirmation_email      = data.get('email') if data.get('confirmation_method') == "Email" else None,
                    appointment_date        = slot_date,
                    appointment_time        = from_time,
                    start_time              = from_time,
                    end_time                = to_time,
                    doctor                  = doctor,
                    customer_message        = data.get('message'),
                    language_pref           = language_pref,
                    specialization          = specialization if specialization else Specializations.objects.get(specialization="No Specialization"),
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
            print('haiiii')
            # Save into DoctorAppointment
            DoctorAppointment.objects.create(
                doctor=doctor,
                specialization=specialization,
                date=Calendar.objects.get_or_create(date=slot_date)[0],
                start_time=from_time,
                end_time=to_time,
                appointment=appointment,
            )
         
            from .tasks import delete_unpaid_appointment
            # delete_unpaid_appointment.apply_async((appointment.appointment_id,), countdown=300)

            return Response({
                'message': 'Appointment successfully booked',
                'appointment': AppointmentHeaderSerializer(appointment).data,
            }, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=400)





from general.models import PreTransactionData

def ConfirmAppointment(appointment_id , pretransaction_id):
    handled = False
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        doctor_appointment = DoctorAppointment.objects.filter(appointment=appointment).first()
        temp_transaction = PreTransactionData.objects.filter(pretransaction_id=pretransaction_id).first()
        customer = appointment.customer
        customer.completed_first_analysis = True
        customer.save() 
    except DoctorAppointment.DoesNotExist:
        appointment.payment_done = True
        appointment.appointment_status = 'pending_slot'
        appointment.status_detail='Payment done but doctor slot was released, due to time limit passed, have to select new slot'
        appointment.save()
        handled=True
    except PreTransactionData.DoesNotExist:
        return Response({"error": "Pretransaction data not found for the given pretransaction ID."}, status=404)
    except AppointmentHeader.DoesNotExist:
        return Response({"error": "Appointment not found for the given appointment ID."}, status=404)
    except CustomerProfile.DoesNotExist:
        return Response({"error": "Customer profile not found for the given appointment ID."}, status=404)

    if not handled:
        appointment.payment_done = True
        appointment.appointment_status = 'confirmed'
        appointment.save()
        doctor_appointment.confirmed = True
        doctor_appointment.save()
        if appointment.confirmation_method == "SMS":
            appointmentbooked(appointment.appointment_id)
        elif appointment.confirmation_method == "Email":
            send_appointment_confirmation_email(
                name=f"{appointment.user.first_name} {appointment.user.last_name}",
                to_email=appointment.email,
                doctor_flag=appointment.doctor.doctor_flag,
                doctor_name=f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
                date=appointment.appointment_date,
                time=appointment.from_time,
                meet_link=appointment.meeting_link
            )
    Transactions.objects.create(
        transaction_id = temp_transaction.pretransaction_id,
        invoice_id = temp_transaction.total_amount,
        trasanction_amount = temp_transaction.total_amount,
        payments_status = "success",
    )



from datetime import datetime, time
from django.db.models import Q
from doctor.models import DoctorAvailableHours, DoctorAppointment, Calendar, DoctorProfiles

def is_doctor_available(doctor_id, date_obj, from_time, to_time):
   

    try:
        # Get the calendar object for the given date
        calendar_obj = Calendar.objects.get(date=date_obj)
    except Calendar.DoesNotExist:
        return False  # No calendar entry for this date

    # Check if the doctor is available at the requested time
    availability_qs = DoctorAvailableHours.objects.filter(
        doctor_id=doctor_id,
        date=calendar_obj,
        start_time__lte=from_time,
        end_time__gte=to_time
    )
    if not availability_qs.exists():
        return False  # Not available in general hours

    # Check if doctor already has a confirmed or pending appointment during this time
    overlapping_appointments = DoctorAppointment.objects.filter(
        doctor_id=doctor_id,
        date=calendar_obj,
        confirmed=True,  # only consider confirmed appointments as blocking
    ).filter(
        Q(start_time__lt=to_time, end_time__gt=from_time)
    )

    return not overlapping_appointments.exists()



def create_action_data_for_pending_appointments(appointment):

    appointment = AppointmentHeader.objects.get(appointment_id = appointment.appointment_id)
    if appointment.appointment_status == "pending_payment":
        try:
            doctor_appointment = DoctorAppointment.objects.filter(appointment=appointment).first()
         
        except DoctorAppointment.DoesNotExist:
            appointment.payment_done = True
            is_doctor_available = is_doctor_available(appointment.doctor.doctor_profile_id ,appointment.appointment_date, appointment.start_time , appointment.end_time)
            if is_doctor_available:
                pass
            handled=True
    return

# class FinalSubmit(CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = CustomerProfileSerializer

#     def post(self, request):
#         user = request.user
#         try:
#             # Extract form data
#             dob = request.data.get('dob')
#             first_name = request.data.get('first_name')
#             last_name = request.data.get('last_name')
#             message = request.data.get('message')
#             preferred_name = request.data.get('preferred_name')
#             slot_id = request.data.get('slot_id')
            
#             confirmation_method = request.data.get('confirmation_method')
#             phone_number = request.data.get('phone_number')
#             email = request.data.get('email')
#             country = request.data.get('country')  
#             if not country:
#                 return Response({'error': 'Country is required'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 try:
#                     country = Countries.objects.get(representation=country)
#                 except Countries.DoesNotExist:
#                     return Response({'error': 'Invalid country '}, status=status.HTTP_400_BAD_REQUEST)
                
#             # Validate required fields
#             required_fields = ['dob', 'first_name', 'last_name', 'slot_id', 'confirmation_method']
#             for field in required_fields:
#                 if not request.data.get(field):
#                     return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

#             # Validate confirmation method
#             if confirmation_method not in ["SMS", "Email", "WhatsApp"]:
#                 return Response({'error': 'Invalid confirmation method'}, status=status.HTTP_400_BAD_REQUEST)
#             if confirmation_method in ["SMS", "WhatsApp"] and not phone_number:
#                 return Response({'error': 'Phone number is required for SMS/WhatsApp'}, status=status.HTTP_400_BAD_REQUEST)
#             if confirmation_method == "Email" and not email:
#                 return Response({'error': 'Email is required for Email confirmation'}, status=status.HTTP_400_BAD_REQUEST)

#             # Update customer profile
#             customerProfile, created = CustomerProfile.objects.get_or_create(user=user)
#             customerProfile.date_of_birth = dob
#             customerProfile.age = calculate_age(dob)
#             customerProfile.preferred_name = preferred_name
#             customerProfile.country_details = country
#             customerProfile.save()

#             # Update user's name
#             user.first_name = first_name
#             user.last_name = last_name
#             user.save()

#             # Update appointment message
#             appointment = AppointmentHeader.objects.filter(customer=customerProfile).first()
#             if not appointment:
#                 return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
                
#             appointment.customer_message = message
#             appointment.appointment_status = 3 
#             appointment.confirmation_method = confirmation_method
#             appointment.confirmation_phone_number = phone_number if confirmation_method in ["SMS", "WhatsApp"] else None
#             appointment.confirmation_email = email if confirmation_method == "Email" else None
#             appointment.save()

#             # Allot doctor
#             try:
#                 appointment_id = self.allot_doctor(request.user.id, customerProfile, slot_id)
#                 appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#                 from_time , to_time =  calculate_from_to_time_with_date(appointment_id)
#                 appointment.meeting_link = generate_google_meet(
#                     summary='appointment_id',
#                     description='Appointment with doctor',
#                     start_time=from_time,
#                     end_time=to_time
#                 )
#                 appointment.save()

#                 response_data = {
#                     'message': 'Personal data submitted successfully',
#                     'appointment': AppointmentHeaderSerializer(appointment).data,
#                 }            
#                 return Response(response_data, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def allot_doctor(self, user_id, customer, slot_id):
#         try:
#             appointment = AppointmentHeader.objects.get(customer=customer)
#             slot = GeneralTimeSlots.objects.get(id=slot_id)
#         except AppointmentHeader.DoesNotExist:
#             raise Exception("Appointment not found.")
#         except GeneralTimeSlots.DoesNotExist:
#             raise Exception("Slot not found.")

#         # Get preferred doctors
#         preferred_doctors = UserPreferredDoctors.objects.filter(user_id=user_id).first()
#         if not preferred_doctors:  
#             raise Exception("Preferred doctors not found.")
            
#         doctor_ids = preferred_doctors.get_doctor_ids()
#         if not doctor_ids:
#             raise Exception("Preferred doctors not available.")

#         # Find available doctor for the given slot
#         for doctor_id in doctor_ids:
#             print("Checking availability for doctor ID:", doctor_id)

#         print("time slot:", slot.from_time, slot.to_time, slot.date.date ,slot.id)
        
#         available_doctor_slot = DoctorAvailableSlots.objects.filter(
#             doctor__doctor_profile_id__in=doctor_ids,
#             is_available=True,
#             time_slot=slot
#         ).select_related('doctor').first()

#         if not available_doctor_slot:
#             raise Exception("No preferred doctor available for this slot.")

#         # Assign doctor to appointment and update availability
#         appointment.doctor = available_doctor_slot.doctor
#         appointment.appointment_status = 4
#         appointment.appointment_slot = available_doctor_slot
#         appointment.appointment_date = slot.date.date
#         appointment.appointment_time = slot.from_time
#         appointment.save()

#         # Mark doctor slot as unavailable
#         available_doctor_slot.is_available = False
#         available_doctor_slot.save()

#         # Send confirmation if needed
#         from general.smss import appointmentbooked
#         if appointment.confirmation_method == "SMS":
#             appointmentbooked(appointment.appointment_id)
            
#         if appointment.confirmation_method == "Email":
#             send_appointment_confirmation_email(
#                 name=f"{customer.user.first_name} {customer.user.last_name}",
#                 to_email=appointment.confirmation_email,
#                 doctor_flag=appointment.doctor.doctor_flag,
#                 doctor_name=f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
#                 date=appointment.appointment_date,
#                 time=appointment.appointment_time,
#                 meet_link=appointment.meeting_link
#             )

#         return appointment.appointment_id 





