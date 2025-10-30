# Django imports
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import ValidationError
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned

# Rest framework imports
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from general.utils import generate_random_otp
# Local app imports
from .models import *
from .serializers import *
from customer.models import *
from customer.serializers import CustomerProfileSerializer
from doctor.models import *
from doctor.slots_service import get_available_slots
from general.emal_service import send_email_verification_otp_email
from general.gmeet.gmeet import generate_google_meet
from general.models import *
from general.models import PreTransactionData
from general.tasks import *
from general.twilio import *
from general.utils import *
from general.whatsapp.whatsapp_messages import send_wa_auth_code

# Python standard library
from dateutil.relativedelta import relativedelta
from datetime import timedelta 

import logging
logger = logging.getLogger(__name__)

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
        logger.info(f"Phone number: {phone_number}")
        logger.info(f"email: {email}")
        otp =generate_random_otp()
        if phone_number:
            if len(str(phone_number))>5:
                logger.info(f"Phone number received and got in: {phone_number}")
                # otp_instance = Phone_OTPs.objects.create(phone=phone_number , otp = '666666')
                   
                try:
                    otp_instance, created = Phone_OTPs.objects.get_or_create(phone=phone_number)
                    otp_instance.otp = otp
                    otp_instance.save()
                except MultipleObjectsReturned:
                    Phone_OTPs.objects.filter(phone=phone_number).delete()
                    otp_instance = Phone_OTPs.objects.create(phone=phone_number, otp=otp)

                # send_otp_sms(otp = otp_instance.otp , to_number=country_code+phone_number)
                send_wa_auth_code(str(country_code)+str(phone_number) , otp_instance.otp)
                logger.info(f"OTP sent to phone number: {phone_number}")
            
        if email:
            # otp_instance = Email_OTPs.objects.create(email=email, otp='666666')
            
            try:
                otp_instance, created = Email_OTPs.objects.get_or_create(email=email)
                otp_instance.otp = otp
                otp_instance.save()
            except MultipleObjectsReturned:
                Email_OTPs.objects.filter(email=email).delete()
                otp_instance = Email_OTPs.objects.create(email=email, otp=otp)

            sg_response =send_email_verification_otp_email(otp = otp_instance.otp , to_email=email , name = 'User')
            logger.info(f"OTP sent to email: {email}")
            logger.info(f"sedgrid response ,{sg_response}")
            
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'email': email
        }) 


# ========API : 2===========/analysis/phone_email_verification/ ========================//
    



User = get_user_model()

class PhoneNumberOrEmailVerificationView(APIView):
    def get_serializer_class(self):
        return None

    def post(self, request):
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        otp = request.data.get('otp')
        timezone = request.data.get('timezone')  # Default to UTC if not provided
        logger.debug(timezone)

        if not otp or (not phone_number and not email):
            return Response({'error': 'Phone number or email and OTP are required.'}, status=HTTP_400_BAD_REQUEST)
        logger.debug(otp)
        user = None
        logger.debug(f'hereeeeeeeee user not found yet {user}')
        logger.debug(f'phone number: {phone_number} here')



        if phone_number :
            logger.debug('phone number got condition 1 passed')
            # if  len(phone_number)<5:
            logger.debug('phone matched and not going for  verification')
            try:
                phone_otp = Phone_OTPs.objects.filter(phone=phone_number, otp=otp).order_by('-created_at').first()
                if not phone_otp:
                    return Response('Invalid otp for phone', status=HTTP_400_BAD_REQUEST)
                logger.debug('verification successfull trying to fetch user')
                # user = User.objects.filter(username=phone_number).first()
                customer = CustomerProfile.objects.filter(whatsapp_number = phone_number).first()

            except Phone_OTPs.DoesNotExist:
                return Response(' Something went wrong please try again', status=HTTP_400_BAD_REQUEST)
                
        # Email OTP verification
        if email:
            try:
                email_otp = Email_OTPs.objects.filter(email=email, otp=otp).order_by('-created_at').first()
                if not email_otp:
                    return Response('Invalid OTP for email', status=HTTP_400_BAD_REQUEST)

                # user = User.objects.filter(email=email).first()
                customer = CustomerProfile.objects.filter(email = email).first()

            except Email_OTPs.DoesNotExist:
                return Response('Something went wrong please try again', status=HTTP_400_BAD_REQUEST)
        if customer:
            user = customer.user
            try :
                logger.debug('user_exists')
                customer_profile = customer
                customer_profile.time_zone = timezone if timezone else 'UTC'
                customer_profile.save()
                logger.debug(f"Customer Profile found: {customer_profile}")
                if customer_profile.completed_first_analysis :
                    exists = True
                elif  customer_profile.partner:
                    if customer_profile.partner.completed_first_analysis:
                        exists = True
                else:
                    exists = False

            except CustomerProfile.DoesNotExist:
                exists = False

            # logger.debug(f"User found: {user.username}")
            # logger.debug(f'user exists {exists}')
            
            # Existing user
            refresh = RefreshToken.for_user(user)
            return Response({
                "country":customer_profile.country_details.country_name if customer_profile.country_details else None,
                "first_analysis_completed":customer_profile.completed_first_analysis,
                'user_exists': exists,
                'verified': True,
                'message': 'Existing user Verified',
                'user_id': user.id,
                'customer_id': customer_profile.id if exists else None,
                'sessionid': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=HTTP_200_OK)
        else:
            # Create new user
            logger.debug("Creating new user")
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
                whatsapp_number = phone_number if phone_number else None,
                completed_first_analysis=False,
                email = email if email else None,
            )
            logger.debug(f"New user created: {user.username}")
            logger.debug(f"Customer Profile created: {customer_profile}")
            customer_profile.time_zone = timezone if timezone else 'UTC'
            customer_profile.save()

            refresh = RefreshToken.for_user(user)
            logger.debug(f"New user created: {user.username}")
            return Response({
                "country":customer_profile.country_details.country_name if customer_profile.country_details else None,
                "first_analysis_completed":customer_profile.completed_first_analysis,
                'user_exists': False,
                'verified': True,
                'message': 'New user created and verified',
                'user_id': user.id,
                'customer_id': customer_profile.id if customer_profile else None,
                'sessionid': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=HTTP_200_OK)




# ========API : 3=========Adding the gender and category of the user for new users and send the questionnaire data based on the gender and cat ========================//
# ========URL : ==========/analysis/submit_gender_category/ ========================//



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
        logger.debug(f"Category ID: {category_id}, Gender: {gender}")
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
            logger.debug(f"Questionnaire: {questionnaire}")
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
        logger.debug(f"Questionnaire data: {questionnaire_serialized}")
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
        timeZone = request.data.get('timezone', 'UTC')  # Default to UTC if not provided
        customer_id  = request.data.get('customer_id',None) 

        logger.debug(country )
        logger.debug(timeZone)
        logger.debug(f"recieved date {preferred_date}")
        logger.debug(f"first_analysis{first_analysis}")
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
            session.preferred_date =  convert_local_dt_to_utc(preferred_date + 'T00:00:00', timeZone) if preferred_date else None
            session.specialization_id = specialization_id
            session.country = country
            session.is_couple = is_couple
            session.is_junior = is_junior
            session.alignment_minutes = alignment_minutes
            session.session_status = "slots_queried"
            session.time_zone = timeZone
            session.save()
        else:
            try:
                country = CustomerProfile.objects.get(id = customer_id).country_details.country_name
                specialization = Specializations.objects.filter(specialization_id = specialization_id).first().specialization
                logger.debug(f"\n\nInside customer profile country fetch analysis views 440  {country} {specialization}")
                country_available = DoctorPaymentRules.objects.filter(country__country_name = country , specialization__specialization =specialization).exists()
                logger.debug(f"\n\nInside country available analysis views 438  {country}: {country_available}")
                if not country_available:
                    logger.debug(f"\n\nInside country not found in analysis views 439  {country}: country changed to US")
                    country = "United States"
            except:
                return Response({"error": "Invalid customer_id"}, status=400)
        try:
            base_date, end_of_base_date = get_current_time_in_utc_from_tz(timeZone)
            # base_date += timedelta(days=1)
            # end_of_base_date += timedelta(days=1)

            if preferred_date:
                try:
                    preferred_dt_start = convert_local_dt_to_utc(f"{preferred_date}T00:00:00", timeZone)
                    preferred_dt_end = convert_local_dt_to_utc(f"{preferred_date}T23:59:59", timeZone)
                except ValueError:
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
            else:
                preferred_dt_start = base_date
                preferred_dt_end = end_of_base_date

        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if not specialization_id or  specialization_id == "No Specialization":
            logger.debug('no Specialization')
            specializations= Specializations.objects.filter(specialization = "No Specialization").first()
            specialization_id =specializations.specialization_id
        if specialization_id:
            specialization = Specializations.objects.filter(specialization_id = specialization_id).first().specialization
        logger.debug(f"\n\n\n preferred_dt_start {preferred_dt_start} {country}")
        logger.debug(f"\n\n\n preferred_dt_end {preferred_dt_end} {country} {specialization}")
        slot_data = get_available_slots(
            specialization_id=specialization_id,
            date_time_start=preferred_dt_start,
            date_time_end=preferred_dt_end,
            buffer = timedelta(hours=6),
            is_couple=is_couple,
            timezone_str = timeZone,
            # alignment_minutes=alignment_minutes,
            is_junior=is_junior,
            gender_info=gender_info,
            language_info=language_info,
            country=country,
            specialization=specialization
        )
        try:
             slot_data["slots"]
        except:
            return Response({"error": "No slots available"}, status=400)
        logger.debug(f"slots_data {slot_data}")
        return Response({   
            "slots": slot_data["slots"],
            "matched_preferences": slot_data["matched_preferences"],
            "gender_matched": slot_data["gender_matched"],
            "language_matched": slot_data["language_matched"],
            "available_dates": slot_data["available_dates"],
            "fallback_message": slot_data["fallback_reason"] or "",
            "doctors_found_but_unavailable": slot_data["doctors_found_but_unavailable"],
            'current_date':slot_data["current_date"],
            "slots_data":slot_data
        }, status=200)


@api_view(['POST'])
def get_multiple_doctor_profiles(request):
    doctor_ids = request.data.get("doctor_ids")
    country = request.data.get("country")
    specialization_id = request.data.get("specialization_id")
    is_couple = request.data.get("is_couple")
    customer_id = request.data.get("customer_id")
    try:
        if not specialization_id : 
            specialization = Specializations.objects.get(specialization = "No Specialization")
        else:
            specialization = Specializations.objects.get(specialization_id =specialization_id)
        logger.debug(f"specialization {specialization}")
        logger.debug(f"\n\nfsafasf {customer_id} fsfsaas")
        logger.debug(f"\n\ncountry {country}")
        if customer_id:
            try:
                country = CustomerProfile.objects.get(id = customer_id).country_details.country_name
                logger.debug(f"country {country}")
            except:
                pass
        country_available = DoctorPaymentRules.objects.filter(country__country_name = country , specialization__specialization =specialization.specialization ,session_count = 1).exists()
        logger.debug(f"\n\ncountry_available {country} {specialization} {country_available}")
        if not country_available:
            logger.debug(f"\n\ninside payment  in country not available {country}")
            country = "United States"
        
    except Specializations.DoesNotExist:
        return Response({'error': 'specialization invalid'}, status=400)
    except CustomerProfile.DoesNotExist:
        return Response({'error': 'customer_id invalid'}, status=400)
        
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
    a_country=country
    for doc in response_data:
        logger.debug(f"\n\nis prescription allowed for doc {doc['name']} {doc['is_prescription_allowed']}")
        if doc['is_prescription_allowed'] :
            a_country = "India"  
            logger.debug(f"\n\ninside condition changed to india {a_country}")
        else:
            logger.debug(f"\n\ninside condition no prescription {a_country}")
            a_country=country
        rule = DoctorPaymentRules.objects.filter(
            doctor__doctor_profile_id=doc['doctor_profile_id'],
            country__country_name=a_country,
            specialization = specialization,
            session_count = 1
        ).first()

        if rule:
            logger.debug(f"\n\n rule . country {rule.country}")
            logger.debug(f"\n\n rule country spec doc {rule.country} {specialization} {doc['doctor_profile_id']}")
        
            if is_couple:
                doc['final_price'] = rule.get_effective_payment()['custom_user_total_fee_couple'] if rule else None
            else:
                logger.debug(f"\n\n rule get_effective_payment {rule.get_effective_payment()}")
                doc['final_price'] = rule.get_effective_payment()['custom_user_total_fee_single'] if rule else None
            doc['country']=rule.country.country_name
            doc['currency']=rule.country.currency
            doc['currency_symbol']=rule.country.currency_symbol

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

class FinalSubmit(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer

    @transaction.atomic
    def post(self, request):
        try:
            user = request.user
            data = request.data

            token = data.get("analysis_token")
            package_id = data.get("package_id")
            include_package = data.get("include_package")
            referral_id = data.get("referal_id")

            # Initialize shared variables
            category = None
            gender_pref = None
            language_pref = None
            specialization = None
            is_couple = False

            package = None
            payment_rule = None
            payment_required = True
            payment_done = False

            # Fetch customer profile
            try:
                customer_profile = CustomerProfile.objects.get(user=user)
            except CustomerProfile.DoesNotExist:
                logger.debug("error Customer profile not found")
                return Response({"error": "Customer profile not found"}, status=400)

            # ====== FIRST ANALYSIS HANDLING ======
            if not customer_profile.completed_first_analysis:
                if not token:
                    return Response({"error": "Missing analysis_token"}, status=400)

                # Get country
                try:
                    country = Countries.objects.get(country_name=data.get("country"))
                except Countries.DoesNotExist:
                    logger.debug("Invalid country")
                    return Response({"error": "Invalid country"}, status=400)

                # Get analysis session
                try:
                    session = AnalysisSession.objects.get(token=token)
                except AnalysisSession.DoesNotExist:
                    logger.debug("Invalid analysis_token")
                    return Response({"error": "Invalid analysis_token"}, status=400)

                # Update profile fields
                customer_profile.gender = data.get("gender")
                customer_profile.date_of_birth = data.get("dob")
                customer_profile.preferred_name = data.get("preferred_name")
                customer_profile.country_details = country
                customer_profile.completed_first_analysis = True
                customer_profile.whatsapp_number = data.get("whatsapp_number")
                customer_profile.mobile_number = data.get("mobile_number")
                customer_profile.mob_country_code = data.get("mob_country_code")
                customer_profile.country_code = data.get("country_code")
                customer_profile.email = data.get("email")
                customer_profile.confirmation_method = data.get("confirmation_method")
                customer_profile.guardian_first_name = data.get("guardian_first_name")
                customer_profile.guardian_last_name = data.get("guardian_last_name")
                customer_profile.guardian_relation = data.get("guardian_relation")
                customer_profile.guardian_phone_number = data.get("guardian_phone_number")
                customer_profile.save()

                user.first_name = data.get("first_name")
                user.last_name = data.get("last_name")
                user.save()

                # Set analysis data
                category = session.category
                gender_pref = session.gender_preference
                language_pref = session.language_preference
                specialization = session.specialization
                is_couple = session.is_couple

                # Attach answers
                AppointmentQuestionsAndAnswers.objects.filter(
                    tempsession=session
                ).update(customer=customer_profile)

                session.status = "final_submitted"
                session.save()

                logger.debug("First Analysis Completed")
            else:
                category = Category.objects.get(id=data.get("category")) if data.get("category") else None
                gender_pref = data.get("gender_pref")
                language_pref = data.get("language_pref")
                specialization = Specializations.objects.get(
                    specialization_id=data.get("specialization")
                ) if data.get("specialization") else None
                is_couple = bool(data.get("is_couple"))

                logger.debug("First Analysis Already Completed")

            # Customer timezone
            timeZone = get_customer_timezone(user)

            # ====== SLOT VALIDATION ======
            slot = data.get("slot", {})
            start_str = slot.get("start")
            end_str = slot.get("end")

            if not all([start_str, end_str]):
                return Response({"error": "Missing slot start/end"}, status=400)

            start_datetime_utc = convert_local_dt_to_utc(start_str, timeZone)
            end_datetime_utc = convert_local_dt_to_utc(end_str, timeZone)

            # Doctor
            try:
                doctor = DoctorProfiles.objects.get(doctor_profile_id=data.get("doctor_id"))
            except DoctorProfiles.DoesNotExist:
                logger.debug("Doctor not found")
                return Response({"error": "Doctor not found"}, status=404)

            # Check for overlap
            overlap_exists = DoctorAppointment.objects.filter(
                doctor=doctor,
                start_time__lt=end_datetime_utc,
                end_time__gt=start_datetime_utc
            ).exists()

            if overlap_exists:
                return Response(
                    {"error": "The selected time slot overlaps with an existing appointment."},
                    status=409
                )

            # ====== PAYMENT / PACKAGE HANDLING ======
            try:
                package = Customer_Package.objects.filter(
                    customer=customer_profile,
                    specialization=specialization,
                    doctor=doctor,
                    is_couple=is_couple,
                    appointments_left__gt=0
                ).first()

                if package:
                    payment_required = False
                    payment_done = True
                    package.appointments_left -= 1
                    package.save()
                else:
                    if include_package:
                        payment_rule = DoctorPaymentRules.objects.get(id=package_id)

            except Exception as e:
                logger.error(f"Error checking package: {e}")

            # ====== CREATE APPOINTMENT ======
            logger.debug(f"gender_pref {gender_pref} language_pref {language_pref} category {category}")
            logger.debug(f"package {package} include_package {include_package} payment_rule {payment_rule}")

            appointment = AppointmentHeader.objects.create(
                customer=customer_profile,
                category=category,
                gender_pref=gender_pref,
                appointment_status='confirmed' if payment_done else "pending_payment",
                status_detail="initiated by customer waiting for payment",
                start_time=start_datetime_utc,
                end_time=end_datetime_utc,
                doctor=doctor,
                customer_message=data.get("message"),
                language_pref=language_pref,
                specialization=specialization or Specializations.objects.get(specialization="No Specialization"),
                is_couple=is_couple,
                referral=Referral.objects.get(id=referral_id) if referral_id else None,
                is_referred=bool(referral_id),
                booked_by="customer",
                payment_required=payment_required,
                payment_done=payment_done,
                package_used=True if package else False,
                payment_rule=payment_rule,
                package_included=bool(include_package),
                package = package if package else None,
            )

            Appointment_customers.objects.create(
                customer=customer_profile,
                appointment=appointment,
            )

            if is_couple:
                if customer_profile.partner:
                    Appointment_customers.objects.get_or_create(
                        customer=customer_profile.partner,
                        appointment=appointment,
                    )

            if referral_id:
                Referral.objects.filter(id=referral_id).update(converted_to_appointment=True)

            DoctorAppointment.objects.create(
                doctor=doctor,
                specialization=appointment.specialization,
                start_time=start_datetime_utc,
                end_time=end_datetime_utc,
                appointment=appointment,
            )

            from .tasks import delete_unpaid_appointment
            delete_unpaid_appointment.apply_async(
                (appointment.appointment_id,),
                countdown=900
            )
            if not payment_required:  
                # Payment not required, so confirm 
                ConfirmAppointment(
                    appointment_id=appointment.appointment_id,
                    pretransaction_id=None,
                    is_admin=True 
                )


            return Response({
                "message": "Appointment successfully booked",
                'payment_required': payment_required,
                "appointment": AppointmentHeaderSerializer(appointment).data,
                "is_couple": appointment.is_couple,
                "doctor_qualification": appointment.doctor.qualification,
                "patient_country": appointment.customer.country_details.country_name
            }, status=201)

        except Exception as e:
            logger.debug(f"Error in FinalSubmit: {str(e)}")
            return Response({"error": str(e)}, status=400)



from django.utils import timezone

# def ConfirmAppointment(appointment_id, pretransaction_id ,is_admin):
#     handled = False
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         doctor_appointment = DoctorAppointment.objects.filter(appointment=appointment).first()
#         if not is_admin:
#             temp_transaction = PreTransactionData.objects.filter(pretransaction_id=pretransaction_id).first()
#         customer = appointment.customer

#         def doctor_released_handler():
#             nonlocal handled
#             overlapping = DoctorAppointment.objects.filter(
#                 doctor=appointment.doctor,
#                 start_time__lt=appointment.end_time,
#                 end_time__gt=appointment.start_time
#             ).exists()

#             if overlapping:
#                 appointment.payment_done = True
#                 appointment.appointment_status = 'pending_slot'
#                 appointment.status_detail = (
#                     "Payment done but doctor slot was released, "
#                     "due to time limit passed and booked by another customer. "
#                     "Customer must select a new slot."
#                 )
#                 appointment.save()
#             elif appointment.start_time - timedelta(hours=1) < timezone.now():
#                 appointment.payment_done = True
#                 appointment.appointment_status = 'pending_slot'
#                 appointment.status_detail = (
#                     "Payment done but the selected slot has already passed. "
#                     "Customer must select a new slot."
#                 )
#                 appointment.save()
#             else:
#                 doctor_appointment = DoctorAppointment.objects.create(
#                     doctor=appointment.doctor,
#                     specialization=appointment.specialization,
#                     start_time=appointment.start_time,
#                     end_time=appointment.end_time,
#                     appointment=appointment,
#                     confirmed=True
#                 )
#                 handled = True
#                 return doctor_appointment
#             return None

#         # Handle missing doctor_appointment
#         if doctor_appointment is None:
#             doctor_appointment = ()

#     except AppointmentHeader.DoesNotExist:
#         return Response({"error": "Appointment not found"}, status=404)
#     except PreTransactionData.DoesNotExist:
#         return Response({"error": "Pretransaction data not found"}, status=404)
#     except CustomerProfile.DoesNotExist:
#         return Response({"error": "Customer profile not found"}, status=404)

#     try:
#         if not handled:
#             appointment.payment_done = True
#             logger.debug("just before confriming")
#             appointment.appointment_status = 'confirmed'
#             appointment.save()
#             logger.debug("\n\n staturs" , appointment.appointment_status , appointment_id , appointment.appointment_id)

#             if doctor_appointment:
#                 doctor_appointment.confirmed = True
#                 doctor_appointment.save()
#             else:
#                 # Safety net: create a DoctorAppointment if missing
#                 doctor_appointment = DoctorAppointment.objects.create(
#                     doctor=appointment.doctor,
#                     specialization=appointment.specialization,
#                     start_time=appointment.start_time,
#                     end_time=appointment.end_time,
#                     appointment=appointment,
#                     confirmed=True
#                 )

#             # Generate meet link
#             aware_from = appointment.start_time if appointment.start_time.tzinfo else timezone.make_aware(appointment.start_time)
#             aware_to = appointment.end_time if appointment.end_time.tzinfo else timezone.make_aware(appointment.end_time)

         

#             appointment.save()

#             appointment_routine_notifications(appointment_id)

#         # Link customer to appointment
#         Appointment_customers.objects.get_or_create(customer=customer, appointment=appointment)

#         # Add partner if couple
#         if appointment.is_couple and customer.partner:
#             Appointment_customers.objects.get_or_create(customer=customer.partner, appointment=appointment)

#         if not handled:
#             meet_details = generate_google_meet(
#                 summary="Appointment",
#                 description="Appointment with doctor",
#                 start_time=aware_from,
#                 end_time=aware_to
#             )
#             track_map_meeting(appointment_id, meet_details["meeting_link"], meet_details["meeting_code"])
#             appointment.meeting_link = meet_details["meeting_link"]

#         # Record transaction
#         if not is_admin:
#             if temp_transaction:
#                 Transactions.objects.create(
#                     pretransaction_data=temp_transaction,
#                     invoice_id=temp_transaction.total_amount,
#                     transaction_amount=temp_transaction.total_amount,
#                     payment_status="success"
#                 )

#         # Handle package if included
#         if appointment.package_included and appointment.payment_rule:
#             package = Customer_Package.objects.create(
#                 customer=customer,
#                 package_name=appointment.payment_rule.pricing_name,
#                 appointments_got=appointment.payment_rule.session_count,
#                 appointments_left=max(0, appointment.payment_rule.session_count - 1),
#                 specialization=appointment.specialization,
#                 doctor=appointment.doctor,
#                 is_couple=appointment.is_couple,
#                 expires_on=timezone.now() + relativedelta(months=appointment.payment_rule.session_count)
#             )
#             appointment.package = package
#             appointment.package_used = True
#             appointment.save() 

#         logger.debug("✅ Appointment confirmed successfully")

#     except Exception as e:
#         import traceback
#         traceback.logger.debug_exc()
#         raise e
















def ConfirmAppointment(appointment_id =None, pretransaction_id =None, is_admin = False):

    logger.debug(f"confirm appointment got called with pre and app , {pretransaction_id} , {appointment_id}")
    try:
        # Step 1: Fetch all necessary objects first
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        doctor_appointment = DoctorAppointment.objects.filter(appointment=appointment).first()
        customer = appointment.customer

        if not is_admin and pretransaction_id:
            pre_transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
        else:
            pre_transaction = None

    except AppointmentHeader.DoesNotExist:
        logger.debug({"error": "Appointment not found"})
        return Response({"error": "Appointment not found"}, status=404)
    except PreTransactionData.DoesNotExist:
        logger.debug({"pre-transaction data not found"})
        return Response({"error": "Pre-transaction data not found"}, status=404)
    except CustomerProfile.DoesNotExist:
        logger.debug({"error": "Customer profile not found"})
        return Response({"error": "Customer profile not found"}, status=404)
    except Exception as e:
        logger.debug({"error": f"An unexpected error occurred during setup: {str(e)}"})
        # Catch any other unexpected errors during object retrieval
        return Response({"error": f"An unexpected error occurred during setup: {str(e)}"}, status=500)

    try:
        # Step 2: Validate slot availability for non-admin confirmations
        # Admins can force confirmation regardless of conflicts
        if not is_admin:
            # Check for overlapping appointments
            overlapping = DoctorAppointment.objects.filter(
                doctor=appointment.doctor,
                start_time__lt=appointment.end_time,
                end_time__gt=appointment.start_time
            ).exclude(appointment=appointment).exists()

                        

            if overlapping:
                appointment.payment_done = True
                appointment.appointment_status = 'pending_slot'
                appointment.status_detail = (
                    "Payment done but doctor slot was released due to time limit passed and "
                    "booked by another customer. Customer must select a new slot."
                )
                appointment.save()
                logger.debug({"message":  "condition one Appointment not confirmed, please select a new slot.", 
                    "select_slots": True})
                return Response({
                    "message": "Appointment not confirmed, please select a new slot.", 
                    "select_slots": True
                }, status=200)

            # Check if the slot has already passed
            if appointment.start_time - timedelta(hours=1) < timezone.now():
                appointment.payment_done = True
                appointment.appointment_status = 'pending_slot'
                appointment.status_detail = (
                    "Payment done but the selected slot has already passed. "
                    "Customer must select a new slot."
                )
                appointment.save()
                logger.debug({"message": "Appointment not confirmed, please select a new slot.", 
                    "select_slots": True})
                return Response({
                    "message": "Appointment not confirmed, please select a new slot.",
                    "select_slots": True
                }, status=200)

        # Step 3: Perform confirmation actions
        appointment.payment_done = True
        appointment.appointment_status = 'confirmed'
        logger.debug(f"appointmrnt_status {appointment.appointment_status}")

        # Step 4: Create/Update DoctorAppointment
        if not doctor_appointment:
            doctor_appointment = DoctorAppointment.objects.create(
                doctor=appointment.doctor,
                specialization=appointment.specialization,
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                appointment=appointment,
                confirmed=True
            )
        else:
            doctor_appointment.confirmed = True
            doctor_appointment.save()

        # Step 5: Link customers
        Appointment_customers.objects.get_or_create(customer=customer, appointment=appointment)
        customer.completed_first_analysis = True
        customer.save()
        if appointment.is_couple and customer.partner:
            Appointment_customers.objects.get_or_create(customer=customer.partner, appointment=appointment)
            customer.partner.completed_first_analysis = True
            customer.partner.save()

        # Step 6: Generate meet link
        aware_from = appointment.start_time if timezone.is_aware(appointment.start_time) else timezone.make_aware(appointment.start_time)
        aware_to = appointment.end_time if timezone.is_aware(appointment.end_time) else timezone.make_aware(appointment.end_time)
        
        meet_details = generate_google_meet(
            summary="Appointment",
            description="Appointment with doctor",
            start_time=aware_from,
            end_time=aware_to
        )
        appointment.meeting_link = meet_details["meeting_link"]
        track_map_meeting(appointment_id, meet_details["meeting_link"], meet_details["meeting_code"])

        # Step 7: Record transaction
        if pre_transaction:
            Transactions.objects.create(
                pretransaction_data=pre_transaction,
                invoice_id=pre_transaction.pretransaction_id, # Changed from amount to ID
                transaction_amount=pre_transaction.total_amount,
                payment_status="success"
            )

        # Step 8: Handle package
        if appointment.package_included and appointment.payment_rule:
            package = Customer_Package.objects.create(
                customer=customer,
                package_name=appointment.payment_rule.pricing_name,
                appointments_got=appointment.payment_rule.session_count,
                appointments_left=max(0, appointment.payment_rule.session_count - 1),
                specialization=appointment.specialization,
                doctor=appointment.doctor,
                is_couple=appointment.is_couple,
                expires_on=timezone.now() + relativedelta(months=appointment.payment_rule.session_count)
            )
            appointment.package = package
            appointment.package_used = True

        # Final save and notifications
        # This is the single, critical save that commits all changes
        appointment.save()
        appointment_routine_notifications(appointment_id)

        # Step 9: Return success response ONLY AFTER all operations are complete
        logger.debug("✅ Appointment confirmed successfully")
        # logger.debug(appointment.appointment_status , appointment_id , appointment.appointment_id)
        logger.debug({"message": "Appointment confirmed successfully.", "select_slots": False, "add_partner": False})
        return Response({"message": "Appointment confirmed successfully.", "select_slots": False, "add_partner": False}, status=200)

    except Exception as e:
        # Generic error handling for the confirmation process
        
        
        logger.exception({"error": f"An error occurred during confirmation: {str(e)}"})
        return Response({"error": f"An error occurred during confirmation: {str(e)}"}, status=500)








from general.notification_controller import send_appointment_confirmation_notification ,schedule_all_reminders





def appointment_routine_notifications(appointment_id):
    logger.debug("inside_routine notifications")

    send_appointment_confirmation_notification.delay(appointment_id)  

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    except AppointmentHeader.DoesNotExist:
        logger.debug("Appointment not found for the given appointment ID.")
        return  # ✅ Exit early

    try:
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except Meeting_Tracker.DoesNotExist:
        logger.debug("Meeting tracker not found for the given appointment ID.")
        return  # ✅ Exit early

    if not appointment.customer.completed_first_analysis:
        appointment.customer.completed_first_analysis = True
        appointment.customer.save()

    logger.debug("sending appointment confirmation notification")

    task = monitor_appointment.apply_async(
        args=[appointment.appointment_id],
        eta=appointment.start_time,
    )

    meeting_tracker.monitor_task_id = task.id

    schedule_all_reminders(appointment_id)

    meeting_tracker.reminder_task_id = task.id
    meeting_tracker.save()
