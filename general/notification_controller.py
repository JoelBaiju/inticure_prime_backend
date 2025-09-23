
from celery import shared_task
from .emal_service import *
from .whatsapp.whatsapp_messages import *
from analysis.models import AppointmentHeader

@shared_task
def send_appointment_cancel_notification(appointment_id):

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment.appointment_id)
        if appointment.customer.confirmation_method in  ['email' ,"Email" , "both" ]:
            send_appointment_cancellation_email(appointment_id)
        if appointment.customer.confirmation_method in  ['whatsapp' ,"Whatsapp" , "both"]:
            send_wa_patient_requested_cancellation(appointment_id)

        send_appointment_cancellation_email_to_specialist(appointment_id)
        send_wa_consultation_canceled_by_patient_to_specialist(appointment_id)

    except AppointmentHeader.DoesNotExist:
        logger.debug(f"Appointment does not exist.for id {appointment.appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.debug(f"Error sending appointment cancel notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment cancel notification."



@shared_task
def send_appointment_confirmation_notification(appointment_id):
    logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id}")
    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        logger.debug(appointment.customer.confirmation_method)
        if appointment.customer.confirmation_method in  ['email' ,"Email" , "both" ]:
            logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id} email")
            if appointment.customer.completed_first_analysis:
                send_appointment_confirmation_customer_email(appointment_id)
            else : 
                send_first_appointment_confirmation_email(appointment_id)
    
    
        if appointment.customer.confirmation_method in  ['whatsapp' ,"WhatsApp" , "both"]:
            logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id} whatsapp")
            if appointment.customer.completed_first_analysis:
                send_wa_appointment_confirmation(appointment_id)
            else:
                send_wa_first_consultation_confirmation(appointment_id)

        send_wa_consultation_confirmation_to_specialist(appointment_id)
        send_appointment_confirmation_doctor_email(appointment_id)

    except AppointmentHeader.DoesNotExist:
        logger.debug(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.debug(f"Error sending appointment confirmation notification for appointment id {appointment_id}: {str(e)}")
        return f"Error sending appointment confirmation notification.{e}"
    


@shared_task
def send_appointment_reshceduled_notification(appointment_id,old_date_time , new_date_time):
    logger.debug(f"send_appointment_reshceduled_notification for appointment id {appointment_id}")

    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        if appointment.customer.confirmation_method in  ['email' ,"Email" , "both" ]:
            send_appointment_rescheduled_email(appointment_id,old_date_time.date(),old_date_time.time(),new_date_time.date() , new_date_time.time())
        if appointment.customer.confirmation_method in  ['whatsapp' ,"WhatsApp" , "both"]:
            pass             
            """ 
                consultation rescheduled wa message for
                patient is mssing have to fix it and add it her 
            """

        send_wa_consultation_rescheduled_by_patient_to_specialist(appointment_id , old_date_time, new_date_time)

    except AppointmentHeader.DoesNotExist:
        logger.debug(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.debug(f"Error sending appointment rescheduled notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment rescheduled notification."
    







@shared_task
def send_doctor_reshceduled_notification(appointment_id):
    logger.debug(f"send_appointment_reshceduled_notification for appointment id {appointment_id}")

    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        if appointment.customer.confirmation_method in  ['email' ,"Email" , "both" ]:
            send_reschedule_request_email(appointment_id)
        if appointment.customer.confirmation_method in  ['whatsapp' ,"WhatsApp" , "both"]:
            send_wa_consultation_rescheduled_by_specialist(appointment_id)             


    except AppointmentHeader.DoesNotExist:
        logger.debug(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.debug(f"Error sending appointment rescheduled notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment rescheduled notification."
    









from celery import shared_task
from django.utils import timezone
from datetime import timedelta




@shared_task
def send_reminder(appointment_id, reminder_type):
   
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    if appointment.appointment_status != "confirmed":
        return
   
    reminder_messages = {
        "one_week": "Your consultation is in one week.",
        "three_days": "Your consultation is in three days.",
        "one_day": "Your consultation is in 24 hours.",
        "one_hour": "Your consultation starts in one hour.",
        "on_time": "Your consultation has started. Please join now.",
    }

    message = reminder_messages.get(reminder_type, "Appointment Reminder")

    if appointment.customer.confirmation_method in  ['email' ,"Email" , "both" ]:
        if appointment.start_time >= timezone.now(): 
            send_appointment_started_reminder_customer_email(appointment_id , message)

        send_appointment_reminder_customer_email(appointment_id , message)
         
    if appointment.customer.confirmation_method in  ['whatsapp' ,"WhatsApp" , "both"]:
        if reminder_type == "one_hour":
            send_wa_consultation_reminder_1_hour_before
        elif reminder_type =="one_day":
            send_wa_consultation_reminder_24_hours_before
    


    
    if appointment.start_time >= timezone.now(): 
        send_appointment_started_reminder_doctor_email(appointment_id , message)
    send_appointment_reminder_doctor_email(appointment_id , message)
    
    if reminder_type == "one_hour":
        send_wa_specialist_reminder_1_hour_before
    elif reminder_type =="one_day":
        """
            missing have to add 
        """
    
    

    send_appointment_reminder_doctor_email( appointment_id , message )


@shared_task
def schedule_all_reminders(appointment_id):
    """
    Schedule all valid reminders for an appointment based on the current time gap.
    """
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

    start_time = appointment.start_time
    now = timezone.now()

    # Define reminder times in descending order
    reminder_offsets = [
        ("one_week", timedelta(days=7)),
        ("three_days", timedelta(days=3)),
        ("one_day", timedelta(days=1)),
        ("one_hour", timedelta(hours=1)),
        ("on_time", timedelta(seconds=0)),
    ]

    for reminder_name, offset in reminder_offsets:
        reminder_time = start_time - offset
        if reminder_time > now:
            # Schedule only future reminders
            send_reminder.apply_async(
                (appointment_id, reminder_name),
                eta=reminder_time
            )


            




from .models import Reminder_Sent_History
from analysis.models import AppointmentHeader


@shared_task
def monitor_appointment(appointment_id):
    logger.debug(appointment_id)
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
def send_payment_pending_notification(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        if appointment.start_time - timedelta(hours=47) > timezone.now():
            if not  appointment.payment_done :
                if appointment.customer.confirmation_method in ["email" , "Email" , "both"]:
                    send_payment_pending_email(
                        appointment_id
                    )
                if appointment.customer.confirmation_method in ["phone" , "Phone" , "both"]:
                    send_wa_payment_pending_reminder(
                        appointment_id
                    )

                send_payment_pending_notification.apply_async((appointment.appointment_id,), countdown=60*60*24)    

        elif appointment.start_time - timedelta(hours=24) > timezone.now():
              if not  appointment.payment_done :
                if appointment.customer.confirmation_method in ["email" , "Email" , "both"]:
                    send_payment_pending_email_final(
                        appointment_id
                    )
                if appointment.customer.confirmation_method in ["WhatsApp" , "whatsapp" , "both"]:
                    send_wa__final_payment_reminder_24_hours_before_consultation_time(
                        appointment_id
                    )

    except Exception as e:
        logger.error(f'Error in send_payment_pending_email_notification: {e}')









from analysis.models import Referral, Referral_customer, AppointmentHeader


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
    if appointment and (appointment.appointment_status != 'confirmed' or "cancelled" not in appointment.appointment_status):

        if appointment.customer.confirmation_method in ["email" , "Email" , "both"]:
            if appointment.start_time - timedelta(hours=47) > timezone.now():
                send_followup_referal_reminder_email(
                    to_email=appointment.customer.email,
                    name=appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
                    specialization=appointment.specialization.specialization,
                    doctor_name=appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
                    doctor_salutation=appointment.doctor.salutation,
                )
                
            elif appointment.start_time - timedelta(hours=24) > timezone.now():
                send_followup_referal_final_reminder_email(
                    to_email=appointment.customer.email,
                    name=appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
                    specialization=appointment.specialization.specialization,
                    doctor_name=appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
                    doctor_salutation=appointment.doctor.salutation,
                )
                Reminder_Sent_History.objects.create(
                    user=appointment.customer.user,
                    user_is_customer=True,
                    appointment=appointment,
                    email=appointment.customer.email,
                    subject='Appointment not scheduled Reminder not final',
                    body=f'You have not scheduled your consultation with {appointment.doctor.first_name} {appointment.doctor.last_name} | {appointment.specialization.specialization}. Please schedule your consultation as soon as possible.',
                )

            if appointment.customer.confirmation_method in ["WhatsApp" , "whatsapp" , "both"]:
                if appointment.start_time - timedelta(hours=47) > timezone.now():
                    send_wa_consultation_reminder_not_yet_scheduled(
                        patient_name=f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}",
                        salutation=appointment.doctor.salutation,
                        specialist_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                        to_phone=f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
                    )

                elif appointment.start_time - timedelta(hours=24) > timezone.now():
                    send_wa_final_consultation_reminder_not_yet_scheduled(
                        patient_name=f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}",
                        salutation=appointment.doctor.salutation,
                        specialist_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                        to_phone=f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
                    )                    
    

    # if appointment and appointment.appointment_status == 'pending_payment':
    #     send_payment_pending_email(
    #         to_email=appointment.customer.email,
    #         name=appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
    #     )
    
    # Handle referral logic
    elif referral and not referral.converted_to_appointment:
        for customer in referal_customers:
            if customer.customer.confirmation_method in ["email" , "Email" , "both"]:
                send_followup_referal_reminder_email(
                    to_email=customer.customer.email,
                    name=customer.customer.user.first_name + ' ' + customer.customer.user.last_name,
                    specialization=referral.specialization.specialization,
                    doctor_name=referral.doctor.first_name + ' ' + referral.doctor.last_name,
                    doctor_salutation=referral.doctor.salutation,
                )
            if customer.customer.confirmation_method in ["WhatsApp" , "whatsapp" , "both"]:
                send_wa_consultation_reminder_not_yet_scheduled(
                    patient_name=f"{customer.customer.user.first_name} {customer.customer.user.last_name}",
                    salutation=referral.doctor.salutation,
                    specialist_name=f"{referral.doctor.first_name} {referral.doctor.last_name}",
                    to_phone=f"{customer.customer.country_code}{customer.customer.whatsapp_number}"
                )
        

