
from celery import shared_task
from .utils import get_meet_logs
from analysis.models import Meeting_Tracker
from django.utils import timezone


@shared_task
def confirm_doctor_customer_attendence(tracker_id):

    tracker = Meeting_Tracker.objects.get(id=tracker_id)
    logs = get_meet_logs(tracker.meeting_code)
    doctor = tracker.appointment.doctor
    customer = tracker.appointment.customer
    doctor_email = doctor.email
    customer_email = customer.email

    if logs:
        for log in logs:
            if log['identifier'] == doctor_email:
                tracker.doctor_attendence_confirmed = True
            elif log['identifier'] == customer_email:
                tracker.customer_attendence_confirmed = True
    tracker.save()





    

# tasks.py
from celery import shared_task
from datetime import datetime, timedelta
from . emal_service import (
    send_appointment_started_reminder_doctor_email , 
    send_appointment_missed_email, 
    send_appointment_started_reminder_customer_email,
    send_doctor_missed_to_customer_email,
    send_followup_referal_reminder_email,
    send_patient_missed_to_doctor_email,    
    send_appointment_reminder_customer_email,
    send_appointment_reminder_doctor_email,
    send_payment_pending_email

    )
from .models import Reminder_Sent_History
from analysis.models import AppointmentHeader


@shared_task
def monitor_appointment(appointment_id):
    print(appointment_id)
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except Meeting_Tracker.DoesNotExist:
        raise Exception('Meeting Tracker does not exist')
    
    
    
    
    if not tracker.doctor_joined:
        
        if appointment.start_time + timedelta(minutes=15) < timezone.now():
            send_appointment_missed_email(
                to_email=tracker.appointment.doctor.email_id,
                patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                doctor_salutation=tracker.appointment.doctor.salutation,
                appointment_id=tracker.appointment.appointment_id,
                doctor_flag=1,
                )
            send_doctor_missed_to_customer_email(
                to_email=tracker.customer_1.email,
                doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                doctor_salutation=tracker.appointment.doctor.salutation,
                patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                appointment_id=tracker.appointment.appointment_id,
                )
            if tracker.customer_2:
                send_doctor_missed_to_customer_email(
                    to_email=tracker.customer_2.email,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                    )
            appointment.appointment_status = 'doctor_missed'
            appointment.save()
            
        else:   
            send_appointment_started_reminder_doctor_email(
                to_email=tracker.appointment.doctor.email_id,
                doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                doctor_salutation=tracker.appointment.doctor.salutation,
                patient_1_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                patient_2_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                date=tracker.appointment.start_time.date().strftime("%B %d, %Y"),
                weekday=tracker.appointment.start_time.date().strftime("%A"),
                time=tracker.appointment.start_time.time().strftime("%I:%M %p"),
                specialization=tracker.appointment.specialization,
                meeting_link=tracker.meeting_link,
            )

        # Save the reminder sent history
            Reminder_Sent_History.objects.create(
                user=tracker.appointment.doctor,
                user_is_customer=False,
                appointment=tracker.appointment,
                email=tracker.appointment.doctor.email_id,
                subject='Appointment Started Reminder',
                body=f'Your appointment with {tracker.customer_1.user.first_name} {tracker.customer_1.user.last_name} has started. Please join the meeting using the link provided.',
            )
    
    if not tracker.customer_1_joined:
        if appointment.start_time + timedelta(minutes=15) < timezone.now():
            send_appointment_missed_email(
                    to_email=tracker.customer_1.email,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                    doctor_flag=0,
                )
            send_patient_missed_to_doctor_email(
                    to_email=tracker.appointment.doctor.email_id,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                )
            appointment.appointment_status = 'customer_missed'
            appointment.save()
        
        else:
            send_appointment_started_reminder_customer_email(
                to_email=tracker.customer_1.user.email,
                doctor_name=tracker.doctor.first_name + ' ' + tracker.doctor.last_name,
                doctor_salutation=tracker.appointment.doctor.salutation,
                patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                date=tracker.appointment.start_time.date().strftime("%B %d, %Y"),
                weekday=tracker.appointment.start_time.date().strftime("%A"),
                time=tracker.appointment.start_time.time().strftime("%I:%M %p"),
                specialization=tracker.appointment.specialization,
                meeting_link=tracker.meeting_link,
            )
            Reminder_Sent_History.objects.create(
                user=tracker.customer_1.user,
                user_is_customer=True,
                appointment=tracker.appointment,
                email=tracker.customer_1.user.email,
                subject='Appointment Started Reminder',
                body=f'Your appointment with {tracker.doctor.first_name} {tracker.doctor.last_name} has started. Please join the meeting using the link provided.',
            )

    
    if tracker.customer_2 and not tracker.customer_2_joined:
        if appointment.start_time + timedelta(minutes=15) < timezone.now():
            send_appointment_missed_email(
                    to_email=tracker.customer_2.email,
                    doctor_name=tracker.doctor.first_name + ' ' + tracker.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                    doctor_flag=0,
                )
            send_patient_missed_to_doctor_email(
                    to_email=tracker.appointment.doctor.email_id,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                )
            appointment.appointment_status = 'customer_missed'
            appointment.save()
        else:

            send_appointment_started_reminder_customer_email(
                to_email=tracker.customer_2.user.email,
                doctor_name=tracker.doctor.first_name + ' ' + tracker.doctor.last_name,
                doctor_salutation=tracker.appointment.doctor.salutation,
                patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                date=tracker.appointment.start_time.date().strftime("%B %d, %Y"),
                weekday=tracker.appointment.start_time.date().strftime("%A"),
                time=tracker.appointment.start_time.time().strftime("%I:%M %p"),
                specialization=tracker.appointment.specialization,
                meeting_link=tracker.meeting_link,
            )

            # Save the reminder sent history
            Reminder_Sent_History.objects.create(
                user=tracker.customer_2.user,
                user_is_customer=True,
                appointment=tracker.appointment,
                email=tracker.customer_2.user.email,
                subject='Appointment Started Reminder',
                body=f'Your appointment with {tracker.doctor.first_name} {tracker.doctor.last_name} has started. Please join the meeting using the link provided.',
            )



    if appointment.start_time + timedelta(minutes=15) < timezone.now():
        return 'Appointment missed'
    # monitor_appointment.apply_async((appointment.appointment_id,), countdown=300)





@shared_task
def schedule_reminder_prior_to_appointment(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except AppointmentHeader.DoesNotExist:
        raise 'Appointment does not exist'
    except Meeting_Tracker.DoesNotExist:
        raise 'Meeting Tracker does not exist'
    
    for customer in appointment.appointment_customers.all():
        meetlink = tracker.customer_1_meeting_link if customer.customer == tracker.customer_1 else tracker.customer_2_meeting_link
        send_appointment_reminder_customer_email(
        to_email=customer.customer.email,
        doctor_name=appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        doctor_salutation=appointment.doctor.salutation,
        c_name=customer.customer.user.first_name + ' ' + customer.customer.user.last_name,
        date=appointment.start_time.date().strftime("%B %d, %Y"),
        weekday=appointment.start_time.date().strftime("%A"),
        time=appointment.start_time.time().strftime("%I:%M %p"),
        specialization=appointment.specialization,
        meeting_link=meetlink,
    )

    
    send_appointment_reminder_doctor_email(
        to_email=tracker.appointment.doctor.email_id,
        doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
        doctor_salutation=tracker.appointment.doctor.salutation,
        date=tracker.appointment.start_time.date().strftime("%B %d, %Y"),
        weekday=tracker.appointment.start_time.date().strftime("%A"),
        time=tracker.appointment.start_time.time().strftime("%I:%M %p"),
        specialization=tracker.appointment.specialization,
        meeting_link=tracker.meeting_link,
        patient_1_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
        patient_2_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name if tracker.customer_2 else None,
    )
    
    

    # schedule_reminder_prior_to_appointment.apply_async((appointment.appointment_id,), countdown=60*60*24)




from analysis.models import Referral, Referral_customer, AppointmentHeader
from celery import shared_task

@shared_task
def schedule_reminder_to_book_appointment(appointment_id=None, referral_id=None):
    appointment = None
    referral = None
    referal_customers = None
    
    try:
        if appointment_id:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        elif referral_id:
            referral = Referral.objects.get(id=referral_id)
            referal_customers = Referral_customer.objects.filter(referral=referral)
        else:
            raise ValueError("Either appointment_id or referral_id must be provided")
            
    except AppointmentHeader.DoesNotExist:
        raise ValueError(f'Appointment with ID {appointment_id} does not exist')
    except Referral.DoesNotExist:
        raise ValueError(f'Referral with ID {referral_id} does not exist')
    except Exception as e:
        raise ValueError(f'Error retrieving data: {str(e)}')
   
    # Handle appointment logic
    if appointment and appointment.appointment_status != 'confirmed':
        for customer in appointment.appointment_customers.all():
            send_followup_referal_reminder_email(
                to_email=customer.customer.email,
                name=customer.customer.user.first_name + ' ' + customer.customer.user.last_name,
                specialization=appointment.specialization.specialization,
                doctor_name=appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
                doctor_salutation=appointment.doctor.salutation,
            )
    
    if appointment and appointment.appointment_status == 'pending_payment':
        send_payment_pending_email(
            to_email=appointment.customer.email,
            name=appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
        )
    
    # Handle referral logic
    elif referral and not referral.converted_to_appointment:
        for customer in referal_customers:
            send_followup_referal_reminder_email(
                to_email=customer.customer.email,
                name=customer.customer.user.first_name + ' ' + customer.customer.user.last_name,
                specialization=referral.specialization.specialization,
                doctor_name=referral.doctor.first_name + ' ' + referral.doctor.last_name,
                doctor_salutation=referral.doctor.salutation,
            )






            


from .emal_service import *
@shared_task
def send_appointment_rescheduled_email_task(appointment_id , previous_date , previous_time , new_date , new_time):
    send_appointment_rescheduled_email(
        appointment_id = appointment_id,
        previous_date = previous_date,
        previous_time = previous_time,
        new_date = new_date,
        new_time = new_time,
    )


@shared_task
def send_appointment_confirmation_customer_email_task(appointment_id):
    send_appointment_confirmation_customer_email(
        appointment_id = appointment_id,
    )

@shared_task
def send_followup_confirmation_email_task(appointment_id):
    send_followup_confirmation_email(
        appointment_id = appointment_id,
    )


@shared_task
def send_first_appointment_confirmation_email_task(appointment_id):
    send_first_appointment_confirmation_email(
        appointment_id = appointment_id,
    )

@shared_task
def send_appointment_cancellation_email_task(appointment_id):
    send_appointment_cancellation_email(
        appointment_id = appointment_id,
    )

@shared_task
def send_doctor_status_email_task(doctor_id):
    send_doctor_status_email(
        doctor_id = doctor_id,
    )



@shared_task
def send_payment_pending_email_task(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    except AppointmentHeader.DoesNotExist:
        return
    if not  appointment.payment_done :
        send_payment_pending_email(
            appointment_id
        )
        # send_payment_pending_email_task.apply_async((appointment.appointment_id,), countdown=60*60*24)


@shared_task
def send_payout_confirmation_email_task(to_email, salutation, doctor_name):
    send_payout_confirmation_email(
        to_email,
        salutation,
        doctor_name,
    )


@shared_task
def send_prescription_email_task(appointment_id ):
    send_prescription_email(
        appointment_id,
    )


@shared_task
def send_reschedule_request_email_task(appointment_id):
    send_reschedule_request_email(
        appointment_id,
    )
