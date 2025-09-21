import profile
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from analysis.models import Appointment_customers, Meeting_Tracker
from general.sendgrid import send_email_via_sendgrid ,send_email_via_smtp
from doctor.models import DoctorProfiles
from inticure_prime_backend.settings import BACKEND_URL
from django.utils import timezone
from analysis.models import AppointmentHeader

import logging
logger = logging.getLogger(__name__)





def send_appointment_cancellation_email(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        print('Sending appointment email failed appointment id invalid')
        return False
    except Meeting_Tracker.DoesNotExist:
        print('Sending appointment email failed meeting tracker not found')
        return False

    subject = "Appointment Cancellation Confirmation - Inticure"
    doctor_salutation = appointment.doctor.salutation

    context = {
        "date":appointment.start_time.date(),
        "time":appointment.start_time.time(),    
        'specialization':appointment.specialization.specialization,
        'doctor_name':appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        "profile_pic":appointment.doctor.profile_pic.url,
        "doctor_bio":appointment.doctor.doctor_bio,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
        'salutation':doctor_salutation,
    }
    for app_customer in appointment_customers:
        context['username'] = app_customer.customer.user.first_name + ' ' + app_customer.customer.user.last_name
        html_content = render_to_string("appointment_cancelled/appointment_cancellation.html", context)
        send_email_via_sendgrid(subject, html_content, app_customer.customer.email)
    return True






def send_appointment_cancellation_email_to_specialist(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        print('Sending appointment email failed appointment id invalid')
        return False
    except Meeting_Tracker.DoesNotExist:
        print('Sending appointment email failed meeting tracker not found')
        return False

    subject = "Appointment Cancellation Confirmation - Inticure"
    doctor_salutation = appointment.doctor.salutation

    context = {
        "date":appointment.start_time.date(),
        "time":appointment.start_time.time(),    
        'specialization':appointment.specialization.specialization,
        'doctor_name':appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        "profile_pic":appointment.doctor.profile_pic.url,
        "doctor_bio":appointment.doctor.doctor_bio,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
        'salutation':doctor_salutation,
    }
    for app_customer in appointment_customers:
        context['username'] = app_customer.customer.user.first_name + ' ' + app_customer.customer.user.last_name
        html_content = render_to_string("appointment_cancelled/appointment_cancelled_to_specialist.html", context)
        send_email_via_sendgrid(subject, html_content, app_customer.customer.email)
    return True







# ==============================================================================================================



def send_followup_confirmation_email(
    appointment_id,
):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        print('Sending follow email failed appointment id invalid')
        return False

    subject = "Follow-up Appointment Confirmation - Inticure"

    context = {
        "date": appointment.start_time.date(),
        "time": appointment.start_time.time(),
        "doctor_name": appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        "specialization": appointment.specialization.specialization,
        "profile_pic": appointment.doctor.profile_pic.url,
        "doctor_bio": appointment.doctor.doctor_bio,
        'specialization':appointment.specialization.specialization,
        'salutation':appointment.doctor.salutation,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
    }
    for app_customer in appointment_customers:
        meetlink = meeting_tracker.customer_1_meeting_link if meeting_tracker.customer_1 == app_customer.customer else meeting_tracker.customer_2_meeting_link
        context['meet_link'] = meetlink
        context['name'] = app_customer.customer.user.first_name + ' ' + app_customer.customer.user.last_name
        html_content = render_to_string("followup_confirmation.html", context)
        send_email_via_sendgrid(subject, html_content, app_customer.customer.email)
    






def send_first_appointment_confirmation_email(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        print('Sending first appointment email failed appointment id invalid')
        return False
    subject = "Appointment Confirmation - Inticure"

    context = {
        "date": appointment.start_time.date(),
        "time": appointment.start_time.time(),
        "doctor_name": appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        'specialization':appointment.specialization.specialization,
        'salutation':appointment.doctor.salutation,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    for app_customer in appointment_customers:
        if not app_customer.customer.completed_first_analysis:
                
            meetlink = meeting_tracker.customer_1_meeting_link if meeting_tracker.customer_1 == app_customer.customer else meeting_tracker.customer_2_meeting_link
            context['name'] = app_customer.customer.user.first_name + ' ' + app_customer.customer.user.last_name
            context['meet_link']=meetlink
            html_content = render_to_string("first_appointment_confirmation_email.html", context)
            send_email_via_sendgrid(subject, html_content, app_customer.customer.email)

    return True






def send_appointment_confirmation_customer_email(appointment_id,):

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        print('Sending appointment email failed appointment id invalid')
        return False

    subject = f"Your Consultation with {appointment.specialization.specialization} {appointment.doctor.first_name + ' ' + appointment.doctor.last_name} is Confirmed"

    
    context = {
        "date": appointment.start_time.date(),
        "time": appointment.start_time.time(),  
        "specialization": appointment.specialization.specialization,
        "doctor_name": appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        "profile_pic": appointment.doctor.profile_pic.url,
        "doctor_bio": appointment.doctor.doctor_bio,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
        'salutation':appointment.doctor.salutation,
    }

    for app_customer in appointment_customers:
        context['name'] = app_customer.customer.user.first_name + ' ' + app_customer.customer.user.last_name
        meetlink = meeting_tracker.customer_1_meeting_link if meeting_tracker.customer_1 == app_customer.customer else meeting_tracker.customer_2_meeting_link
        context['meet_link']=meetlink
        html_content = render_to_string("appointment_confirmation_customer.html", context)
        send_email_via_sendgrid(subject, html_content, app_customer.customer.email)
    return True





def send_appointment_confirmation_doctor_email(appointment_id,):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)

        context = {
            "date": appointment.start_time.date(),
            "time": appointment.start_time.time(),
            "specialization": appointment.specialization.specialization,
            "doctor_name": appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
            'backend_url':BACKEND_URL,  
            "meet_link":meeting_tracker.doctor_meeting_link
        }
        subject = "Consultation Confirmed"
        html_content = render_to_string("appointment_confirmation_doctor.html", context)
        send_email_via_sendgrid(subject, html_content, appointment.doctor.email_id)
    except AppointmentHeader.DoesNotExist:
        print('Sending appointment email failed appointment id invalid')
        return False




# ==============================================================================================================


def send_appointment_rescheduled_email(
    appointment_id , previous_date,previous_time,new_date,new_time
):

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
            return False
    subject = "Appointment Rescheduled - Inticure"
    
    for customer in appointment_customers:
        meetlink = meeting_tracker.customer_1_meeting_link if customer.customer == meeting_tracker.customer_1 else meeting_tracker.customer_2_meeting_link
        context = {
            "name": customer.customer.user.first_name + ' ' + customer.customer.user.last_name,
            "doctor_name": appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
            "specialization": appointment.specialization.specialization,
            "meet_link": meetlink,
            "appointment_id": appointment_id,
            "doctor_flag": 0,
            # Adding formatted date and time for easier template usage
            "previous_date":previous_date,
            "previous_time":previous_time,
            "new_date":new_date,
            "new_time":new_time,
            'year':timezone.now().year,
            'backend_url':BACKEND_URL,  
            'salutation':appointment.doctor.salutation,
        }
        # Render HTML template with context
        html_content = render_to_string("order_reschedule.html", context)

        send_email_via_sendgrid(subject, html_content, customer.customer.email)

    context['doctor_flag'] = 1
    html_content = render_to_string("order_reschedule.html", context)
    send_email_via_sendgrid(subject, html_content, appointment.doctor.email_id)
    return True




def send_reschedule_request_email(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        appointment_customers = Appointment_customers.objects.filter(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        return
    subject = "Doctor Emergency – Please Reschedule Your Appointment"

    context = {
        "date": appointment.start_time.date(),
        "time": appointment.start_time.time(),
        "doctor_name": appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        "salutation": appointment.doctor.salutation, 
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  
    }
    for customer in appointment_customers:
        context['name'] = customer.customer.user.first_name + ' ' + customer.customer.user.last_name
        html_content = render_to_string("reschedule_request.html", context)

        send_email_via_sendgrid(subject, html_content, customer.customer.email)


# =====================================================================================================================



def send_doctor_status_email(doctor_id):
    try:
        doctor = DoctorProfiles.objects.get(doctor_profile_id = doctor_id)
    except DoctorProfiles.DoesNotExist:
        return
    
    subject = "Welcome to Inticure!" if doctor.is_accepted else "Your Inticure Application Status"

    context = {
        "is_accepted": doctor.is_accepted,
        "salutation": doctor.salutation,
        "doctor_name": doctor.first_name + ' ' + doctor.last_name,
        'backend_url':BACKEND_URL
    }

    html_content = render_to_string("doctor_status.html", context)
    return send_email_via_sendgrid(subject, html_content, doctor.email_id)







from datetime import datetime

def send_appointment_reminder_customer_email(appintment_id , message):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appintment_id)
        appointment_customers = appointment.appointment_customers.all()
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        for customer in appointment_customers:
            meeting_link = meeting_tracker.customer_1_meeting_link if customer.customer == meeting_tracker.customer_1 else meeting_tracker.customer_2_meeting_link

            context = {
                "message":message,
                "c_name": customer.customer.user.first_name,
                "date" : appointment.start_time.strftime("%B %d, %Y"),
                "weekday" : appointment.start_time.strftime("%A"),
                "time" : appointment.start_time.strftime("%I:%M %p"),
                "meeting_link": meeting_link,
                "year": timezone.now().year,
                'doctor_name':f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                'salutation':appointment.doctor.salutation,
                'specialization':appointment.specialization.specialization,
                'backend_url':BACKEND_URL,
            }
            subject = f"Reminder: {message}"
            html_content = render_to_string("appointment_reminder/appointment_reminder_customer.html", context)
            send_email_via_sendgrid(subject, html_content, customer.customer.email)

    except Exception as e:
        logger.debug(f"appointment_reminder_customer Email not sent error{e}")
        return f"appointment_reminder_customer Email not sent error{e}"
    

def send_appointment_reminder_doctor_email(appointment_id , message):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        
        context = {
            "message":message,
            "patient_1_name": f"{meeting_tracker.customer_1.user.first_name} {meeting_tracker.customer_2.user.last_name}",
            "patient_2_name": f"{meeting_tracker.customer_2.user.first_name} {meeting_tracker.customer_2.user.last_name}",
            "date" : appointment.start_time.strftime("%B %d, %Y"),
            "weekday" : appointment.start_time.strftime("%A"),
            "time" : appointment.start_time.strftime("%I:%M %p"),
            "meeting_link": meeting_tracker.doctor_meeting_link,
            "year": timezone.now().year,
            'doctor_name':f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
            'salutation':appointment.doctor.salutation,
            'specialization':appointment.specialization.specialization,    
            'backend_url':BACKEND_URL,
        }

        html_content = render_to_string("appointment_reminder/appointment_reminder_doctor.html", context)
        subject = f"Reminder: {message} with {context['patient_1_name']}"
        return send_email_via_sendgrid(subject, html_content , appointment.doctor.email_id)
    
    except Exception as e:
        logger.debug(f"appointment_reminder_doctor Email not sent error{e}")
        return f"appointment_reminder_doctor Email not sent error{e}"

from datetime import datetime
from django.template.loader import render_to_string

def send_appointment_started_reminder_doctor_email(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        doctor = appointment.doctor

        context = {
            "doctor_name": f"{doctor.first_name} {doctor.last_name}",
            'salutation':doctor.salutation,
            "patient_1_name": f"{meeting_tracker.customer_1.user.first_name} {meeting_tracker.customer_1.user.last_name}",
            "patient_2_name": f"{meeting_tracker.customer_2.user.first_name} {meeting_tracker.customer_2.user.last_name}",
            "date": appointment.start_time.strftime("%B %d, %Y"),
            "weekday": appointment.start_time.strftime("%A"),
            "time": appointment.start_time.strftime("%I:%M %p"),
            "specialization": appointment.specialization.specialization,
            "meeting_link": meeting_tracker.doctor_meeting_link,
            "year": timezone.now().year,
            'backend_url':BACKEND_URL,
        }

        subject = f"Reminder: Your Consultation with {context['patient_1_name']} has started"

        html_content = render_to_string("appointment_reminder/appointment_started_reminder_doctor.html", context)

        return send_email_via_sendgrid(subject, html_content, doctor.email_id)

    except Exception as e:
        logger.debug(f"send_appointment_started_reminder_doctor_email Email not sent error{e}")
        return f"send_appointment_started_reminder_doctor_email Email not sent error{e}"





def send_appointment_started_reminder_customer_email(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        appt_customers = appointment.appointment_customers.all()
        for customer in appt_customers:
            meeting_link = meeting_tracker.customer_1_meeting_link if customer.customer == meeting_tracker.customer_1 else meeting_tracker.customer_2_meeting_link
            context = {
                "doctor_name": f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                "patient_name": f"{customer.customer.user.first_name} {customer.customer.user.last_name}",
                'salutation':appointment.doctor.salutation,
                "date": appointment.start_time.strftime("%B %d, %Y"),
                "weekday": appointment.start_time.strftime("%A"),
                "time": appointment.start_time.strftime("%I:%M %p"),
                "specialization": appointment.specialization.specialization,
                "meeting_link": meeting_link,
                "year": timezone.now().year,
                'backend_url':BACKEND_URL,
            }
            subject = f"Reminder: Your Consultation with {context['doctor_name']} has started"
            html_content = render_to_string("appointment_reminder/appointment_started_reminder_customer.html", context)
            send_email_via_sendgrid(subject, html_content, customer.customer.email_id)
    except Exception as e:
        logger.debug(f"send_appointment_started_reminder_customer_email Email not sent error{e}")
        return f"send_appointment_started_reminder_customer_email Email not sent error{e}"









from datetime import datetime
from django.template.loader import render_to_string

def send_appointment_missed_email(
    to_email, doctor_name, patient_name, doctor_flag, appointment_id=None,doctor_salutation=None
):
    """
    doctor_flag = 0 → patient version
    doctor_flag = 1 → doctor version
    """

    # Subject changes depending on recipient type
    if doctor_flag == 0:
        subject = "Notification: You Missed Your Appointment"
    else:
        subject = f"Notification: Appointment #{appointment_id} Marked as No-Show"

    context = {
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        'salutation':doctor_salutation,
        "doctor_flag": doctor_flag,
        "appointment_id": appointment_id,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,
    }

    html_content = render_to_string("appointment_missed/appt_no_show.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)


def send_doctor_missed_to_customer_email(
    to_email, doctor_name, patient_name, appointment_id,doctor_salutation=None
):
    subject = f"Notification: Appointment #{appointment_id} Marked as No-Show"

    context = {
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        "appointment_id": appointment_id,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,
        'salutation':doctor_salutation,
    }

    html_content = render_to_string("appointment_missed/doctor_missed_for_customer.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)


def send_patient_missed_to_doctor_email(
    to_email, doctor_name, patient_name, appointment_id,doctor_salutation=None
):
    subject = f"Notification: Appointment #{appointment_id} Marked as No-Show"

    context = {
        'backend_url':BACKEND_URL,
        'salutation':doctor_salutation,
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        "appointment_id": appointment_id,
        "year": timezone.now().year,
    }

    html_content = render_to_string("appointment_missed/customer_missed_for_doctor.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)






def send_email_verification_otp_email(to_email, name, otp):
    subject = "Verify Your Email - Inticure"
    logger.debug(f"inside send email function to_email: {to_email}, name: {name}, otp: {otp}")
    logger.info(BACKEND_URL)
    context = {
        "name": name,
        "otp": otp,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    html_content = render_to_string("email_otp.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)





def send_followup_referal_reminder_email(to_email, name, specialization,doctor_name,doctor_salutation=None):
    subject = f"Reminder: Schedule Your {specialization} Consultation with Inticure"

    context = {
        "name": name,
        "specialization": specialization,
        "doctor_name":doctor_name,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
        'salutation':doctor_salutation,
    }

    html_content = render_to_string("appointment_reminder/followup_reminder.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)



def send_followup_referal_final_reminder_email(to_email, name, specialization,doctor_name,doctor_salutation=None):
    subject = f"Reminder: Schedule Your {specialization} Consultation with Inticure"

    context = {
        "name": name,
        "specialization": specialization,
        "doctor_name":doctor_name,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
        'salutation':doctor_salutation,
        'final':True,
    }

    html_content = render_to_string("appointment_reminder/followup_reminder.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)







from datetime import datetime
from django.template.loader import render_to_string

def send_payment_pending_email(appointment_id):
    
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    except AppointmentHeader.DoesNotExist:
        return
    subject = "Action Required: Complete Payment to Confirm Your Consultation"

    context = {
        "name": appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  


    }
    # Render HTML template with context
    html_content = render_to_string("payment_mail.html", context)

    if appointment.appointment_status != 'confirmed':
        send_email_via_sendgrid(subject, html_content, appointment.customer.email)
        

def send_payment_pending_email_final(appointment_id):
    
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    except AppointmentHeader.DoesNotExist:
        return
    subject = "Action Required: Complete Payment to Confirm Your Consultation"

    context = {
        "name": appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  
    }
    # Render HTML template with context
    html_content = render_to_string("payment_mail_final_24_before.html", context)

    if appointment.appointment_status != 'confirmed':
        send_email_via_sendgrid(subject, html_content, appointment.customer.email)
        


from datetime import datetime
from django.template.loader import render_to_string

def send_payout_confirmation_email(to_email, doctor_salutation, doctor_name):
    """
    Sends an email notification to a doctor when payment has been successfully processed.
    
    Args:
        to_email: Recipient email address (doctor's email)
        doctor_salutation: Salutation for the doctor (e.g., Dr., Mr., Ms.)
        doctor_name: Name of the doctor
    """
    subject = "Payment Confirmation - Inticure"

    context = {
        "salutation": doctor_salutation,
        "doctor_name": doctor_name,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    html_content = render_to_string("payout_confirm.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)




from django.template.loader import render_to_string

def send_prescription_email(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    except AppointmentHeader.DoesNotExist:
        return
    subject = "Your Prescription is Ready - Inticure"

    context = {
        "name": appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    # Render HTML email content
    html_content = render_to_string("prescriptions.html", context)

    return send_email_via_sendgrid(subject, html_content, appointment.customer.email)


from django.template.loader import render_to_string

def send_refund_complete_email(to_email, name):
    """
    Sends refund complete notification email.

    Args:
        to_email: Recipient email address
        name: Recipient's name for personalization
    """
    subject = "Refund Processed - Inticure"

    context = {
        "name": name,
        'year':timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    # Render HTML content from template
    html_content = render_to_string("refund_completed.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)


from django.template.loader import render_to_string
from datetime import datetime

def send_report_email(to_email, doctor_flag, name, doctor_salutation=None, doctor_name=None):
    """
    Sends inappropriate behavior warning email to either patient or doctor.

    Args:
        to_email: Recipient email address
        doctor_flag: 0 if sending to patient, 1 if sending to doctor
        name: Patient's name
        doctor_salutation: Doctor's salutation (e.g., Dr., Prof.) - required if doctor_flag = 1
        doctor_name: Doctor's name - required if doctor_flag = 1
    """
    subject = (
        "Important: Behavior Warning Notification"
        if doctor_flag == 0 else
        "Report Acknowledgement - Inticure"
    )

    context = {
        "doctor_flag": doctor_flag,
        "name": name,
        "salutation": doctor_salutation,
        "doctor_name": doctor_name,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    html_content = render_to_string("report_customer.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)




from django.template.loader import render_to_string
from datetime import datetime



from datetime import datetime

def send_user_banned_email(to_email):
    """
    Sends an account suspension email notification.

    Args:
        to_email: Recipient email address (string)
    """
    subject = "Important Notice – Your Inticure Account Has Been Suspended"

    context = {
        "email": to_email,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    html_content = render_to_string("user_banned.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)




from django.template.loader import render_to_string
from datetime import datetime

def send_user_confirmation_email(to_email):
    """
    Sends account confirmation / welcome email.

    Args:
        to_email (str): Recipient email address
    """
    subject = "Welcome to Inticure – Confirm Your Account"

    context = {
        "email": to_email,
        "year": timezone.now().year,
        'backend_url':BACKEND_URL,  
    }

    html_content = render_to_string("user_confirmation.html", context)

    return send_email_via_sendgrid(subject, html_content, to_email)
