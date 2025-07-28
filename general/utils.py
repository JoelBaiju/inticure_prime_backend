
import secrets
import string
from django.conf import settings


def generate_random_otp(length=6):
    otp=''.join(secrets.choice(string.digits) for _ in range(length))
    print(otp)
    return otp







from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from .sendgrid import send_mail
def send_otp_email(firstname,otp,toemail):
    # send_mail(
    #     body=render_to_string('email_otp.html', {
    #         'name': firstname,
    #         'otp': otp
    #     }),
    #     to_email=toemail
    # )

    try:

        subject = 'Your OTP for Email Verification'
        html_message = render_to_string('email_otp.html', {
        'name': firstname,
        'otp': otp
        })
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,  # Use the default from email
        [toemail]    
        )
        email.attach_alternative(html_message, 'text/html')
        print(f"Sending OTP email to {toemail}")
        print(email.send())
    
    except Exception as e:
        print(f"Failed to send OTP email to {toemail}: {str(e)}")
        print(f"Email sending failed: {e}")





from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_appointment_confirmation_email(
    name,
    date,
    time,
    doctor_name,
    meet_link,
    to_email,
    doctor_flag=0
):
  
    subject = 'Your Appointment Confirmation with Inticure'
    
    # Render the HTML template with all parameters
    html_message = render_to_string('order_confirmation_customer.html', {
        'doctor_flag': doctor_flag,
        'name': name,
        'date': date,
        'time': time,
        'doctor_name': doctor_name,
        'meet_link': meet_link
    })
    
    # Create plain text version by stripping HTML tags
    plain_message = strip_tags(html_message)
    
    # Create the email object
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email]
    )
    
    # Attach the HTML version
    email.attach_alternative(html_message, 'text/html')
    
    try:
        # Send the email
        result = email.send()
        print(f"Appointment confirmation email sent to {to_email}. Result: {result}")
        return result
    except Exception as e:
        print(f"Failed to send appointment confirmation email to {to_email}. Error: {str(e)}")
        return False
    








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import datetime, timedelta
from django.db.models import Q
from django.core.cache import cache
from general.models import UserPreferredDoctors
from doctor.models import DoctorProfiles
from doctor.models import GeneralTimeSlots , DoctorPaymentRules
from general.models import UserPreferredDoctors


def filter_doctors_based_on_preference( gender_info  , language_info ,user_id , country , specialization):
    print('helooo')
    gender = gender_info.get('value')
    gender_priority = int(gender_info.get('priority', 0)) if gender_info else 0

    language = language_info.get('value')
    language_priority = int(language_info.get('priority', 0)) if language_info else 0
   

    q_gender = Q(gender=gender) if gender else Q()
    q_language = Q(known_languages__language__language__iexact=language) if language else Q()

    doctors = DoctorProfiles.objects.filter(
        doctor_flag="junior",
        is_accepted=True,
        payment_assignments__country__country_name=country,
        payment_assignments__specialization__specialization=specialization
    ).distinct()

    print('gender' , gender , 'gender_priority' , gender_priority)
    print('lang', language , 'language_priority' , language_priority)

    gender_matched = False
    language_matched = False
    preferred_doctors = DoctorProfiles.objects.none()
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


    user_preferred_doctors, created = UserPreferredDoctors.objects.get_or_create(user_id=user_id)


    if preferred_doctors:
        preferred_doctor_ids = list(preferred_doctors.values_list('doctor_profile_id', flat=True))
        
        if created:
            for doctor_id in preferred_doctor_ids:
                user_preferred_doctors.add_doctor(doctor_id)
        else:
            user_preferred_doctors.clear_doctors()
            for doctor_id in preferred_doctor_ids:
                user_preferred_doctors.add_doctor(doctor_id)
        user_preferred_doctors.save()

    else:
        preferred_doctor_ids = None

    print("haiii")

    return preferred_doctors , preferred_doctor_ids , gender_matched, language_matched , user_preferred_doctors.id





def filter_slots_based_on_preferred_doctors(preferred_doctors, base_date , preferred_date):

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
            date__date=current_date
        ).select_related('date').distinct()

        if slots_today.exists() and matched_slots is None:
            matched_slots = slots_today
            matched_date = current_date

        if slots_today.exists():
            if preferred_date and current_date == preferred_date:
                # If preferred date matches, we can add the slots of that date
                matched_slots = slots_today
                matched_date = current_date
                all_available_dates.append(str(current_date))

        current_date += timedelta(days=1)

    return matched_slots ,  matched_date, all_available_dates









def calculate_age(birth_date):
    """
    Calculate age based on the birth date.
    :param birth_date: Birth date in 'YYYY-MM-DD' format.
    :return: Age in years.
    """
    from datetime import datetime
    today = datetime.today()
    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

from datetime import datetime, timedelta, time

def calculate_from_to_time_with_date(appointment_id):
    """
    Calculate the from and to time for an appointment based on the appointment ID.
    Returns datetime objects suitable for Google Meet.
    :param appointment_id: The ID of the appointment.
    :return: A tuple containing the from and to datetime objects.
    """
    from analysis.models import AppointmentHeader
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    
    if not appointment:
        return None, None
    
    # Get the appointment date and time
    appointment_date = appointment.appointment_date
    appointment_time = appointment.appointment_time
    
    # Combine date and time to create a datetime object
    from_datetime = datetime.combine(appointment_date, appointment_time)
    
    # Calculate duration (default to 1 hour if not specified)
    duration = appointment.duration if hasattr(appointment, 'duration') and appointment.duration else timedelta(hours=1)
    
    # Calculate end time
    to_datetime = from_datetime + duration
    
    return from_datetime, to_datetime