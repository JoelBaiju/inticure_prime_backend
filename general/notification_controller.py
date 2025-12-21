from celery import shared_task
from .emal_service import *
from .whatsapp.whatsapp_messages import *
from analysis.models import AppointmentHeader

import logging
logger = logging.getLogger(__name__)


@shared_task
def send_appointment_cancel_notification(appointment_id):
    """Send cancellation notifications with proper error handling."""
    logger.debug("inside appointment cancelled notification")
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        
        # Customer notifications
        try:
            if appointment.customer.confirmation_method in ['email', "Email", "both"]:
                logger.debug(f"send_appointment_cancellation_email for appointment id {appointment_id} email")
                logger.debug(send_appointment_cancellation_email(appointment_id))
        except Exception as e:
            logger.error(f"Error sending cancellation email to customer for appointment {appointment_id}: {str(e)}")
        
        try:
            if appointment.customer.confirmation_method in ['whatsapp', "Whatsapp", "both"]:
                logger.debug(f"send_appointment_cancellation_whatsapp for appointment id {appointment_id}")
                logger.debug(send_wa_patient_requested_cancellation(appointment_id))
        except Exception as e:
            logger.error(f"Error sending cancellation WhatsApp to customer for appointment {appointment_id}: {str(e)}")
        
        # Admin notifications
        try:
            logger.debug(f"send_appointment_cancellation_email_to_admin for appointment id {appointment_id}")
            logger.debug(send_appointment_cancellation_email_to_admin(appointment_id))
        except Exception as e:
            logger.error(f"Error sending cancellation email to admin for appointment {appointment_id}: {str(e)}")
        
        try:
            logger.debug(f"send_wa_consultation_cancelled_to_admin for appointment id {appointment_id}")
            logger.debug(send_wa_consultation_cancelled_to_admin(appointment_id))
        except Exception as e:
            logger.error(f"Error sending cancellation WhatsApp to admin for appointment {appointment_id}: {str(e)}")
        
        # Specialist notifications
        try:
            logger.debug(f"send_appointment_cancellation_email_to_specialist for appointment id {appointment_id}")
            logger.debug(send_appointment_cancellation_email_to_specialist(appointment_id))
        except Exception as e:
            logger.error(f"Error sending cancellation email to specialist for appointment {appointment_id}: {str(e)}")
        
        try:
            logger.debug(f"send_wa_consultation_canceled_by_patient_to_specialist for appointment id {appointment_id}")
            logger.debug(send_wa_consultation_canceled_by_patient_to_specialist(appointment_id))
        except Exception as e:
            logger.error(f"Error sending cancellation WhatsApp to specialist for appointment {appointment_id}: {str(e)}")
        
        return "Cancellation notifications sent successfully"

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.error(f"Error sending appointment cancel notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment cancel notification."


@shared_task
def send_appointment_confirmation_notification(appointment_id):
    """Send confirmation notifications with proper error handling."""
    logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id}")

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        logger.debug(appointment.customer.confirmation_method)
        
        # Customer email notifications
        try:
            if appointment.customer.confirmation_method in ['email', "Email", "both"]:
                logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id} email")
                if appointment.customer.completed_first_analysis:
                    send_appointment_confirmation_customer_email(appointment_id)
                else:
                    send_first_appointment_confirmation_email(appointment_id)
        except Exception as e:
            logger.error(f"Error sending confirmation email to customer for appointment {appointment_id}: {str(e)}")
        
        # Customer WhatsApp notifications
        try:
            if appointment.customer.confirmation_method in ['whatsapp', "WhatsApp", "both"]:
                logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id} whatsapp")
                if appointment.customer.completed_first_analysis:
                    logger.debug(send_wa_appointment_confirmation(appointment_id))
                else:
                    logger.debug(f"send_appointment_confirmation_notification for appointment id {appointment_id} whatsapp first consultation")
                    logger.debug(send_wa_first_consultation_confirmation(appointment_id))
        except Exception as e:
            logger.error(f"Error sending confirmation WhatsApp to customer for appointment {appointment_id}: {str(e)}")
        
        # Specialist notifications
        try:
            send_wa_consultation_confirmation_to_specialist(appointment_id)
        except Exception as e:
            logger.error(f"Error sending confirmation WhatsApp to specialist for appointment {appointment_id}: {str(e)}")
        
        try:
            send_appointment_confirmation_doctor_email(appointment_id)
        except Exception as e:
            logger.error(f"Error sending confirmation email to doctor for appointment {appointment_id}: {str(e)}")
        
        # Admin notifications
        try:
            send_wa_consultation_confirmation_to_admin(appointment_id)
        except Exception as e:
            logger.error(f"Error sending confirmation WhatsApp to admin for appointment {appointment_id}: {str(e)}")
        
        try:
            send_appointment_confirmation_email_to_admin(appointment_id)
        except Exception as e:
            logger.error(f"Error sending confirmation email to admin for appointment {appointment_id}: {str(e)}")
        
        return "Confirmation notifications sent successfully"
    
    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.error(f"Error sending appointment confirmation notification for appointment id {appointment_id}: {str(e)}")
        return f"Error sending appointment confirmation notification.{e}"


@shared_task
def send_appointment_reshceduled_notification(appointment_id, old_date_time, new_date_time):
    """Send rescheduled notifications with proper error handling."""
    logger.debug(f"send_appointment_reshceduled_notification for appointment id {appointment_id}")

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        
        # Customer email notification
        try:
            if appointment.customer.confirmation_method in ['email', "Email", "both"]:
                send_appointment_rescheduled_email(
                    appointment_id,
                    old_date_time.date(),
                    old_date_time.time(),
                    new_date_time.date(),
                    new_date_time.time()
                )
        except Exception as e:
            logger.error(f"Error sending rescheduled email to customer for appointment {appointment_id}: {str(e)}")
        
        # Customer WhatsApp notification
        try:
            if appointment.customer.confirmation_method in ['whatsapp', "WhatsApp", "both"]:
                pass
                """ 
                    consultation rescheduled wa message for
                    patient is missing have to fix it and add it here 
                """
        except Exception as e:
            logger.error(f"Error sending rescheduled WhatsApp to customer for appointment {appointment_id}: {str(e)}")
        
        # Specialist notification
        try:
            send_wa_consultation_rescheduled_by_patient_to_specialist(appointment_id, old_date_time, new_date_time)
        except Exception as e:
            logger.error(f"Error sending rescheduled WhatsApp to specialist for appointment {appointment_id}: {str(e)}")
        
        # Admin notifications
        try:
            send_appointment_rescheduled_email_admin(
                appointment_id,
                old_date_time.date(),
                old_date_time.time(),
                new_date_time.date(),
                new_date_time.time()
            )
        except Exception as e:
            logger.error(f"Error sending rescheduled email to admin for appointment {appointment_id}: {str(e)}")
        
        try:
            send_wa_consultation_rescheduled_admin_notification(appointment_id)
        except Exception as e:
            logger.error(f"Error sending rescheduled WhatsApp to admin for appointment {appointment_id}: {str(e)}")
        
        return "Rescheduled notifications sent successfully"
        
    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.error(f"Error sending appointment rescheduled notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment rescheduled notification."


@shared_task
def send_doctor_reshceduled_notification(appointment_id):
    """Send doctor rescheduled notifications with proper error handling."""
    logger.debug(f"send_doctor_reshceduled_notification for appointment id {appointment_id}")

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        
        # Customer email notification
        try:
            if appointment.customer.confirmation_method in ['email', "Email", "both"]:
                logger.debug(f"send_doctor_reshceduled_notification for appointment id {appointment_id} email")
                logger.debug(send_reschedule_request_email(appointment_id))
        except Exception as e:
            logger.error(f"Error sending doctor reschedule email to customer for appointment {appointment_id}: {str(e)}")
        
        # Customer WhatsApp notification
        try:
            if appointment.customer.confirmation_method in ['whatsapp', "WhatsApp", "both"]:
                logger.debug(f"send_doctor_reshceduled_notification for appointment id {appointment_id} whatsapp")
                logger.debug(send_wa_consultation_rescheduled_by_specialist(appointment_id))
        except Exception as e:
            logger.error(f"Error sending doctor reschedule WhatsApp to customer for appointment {appointment_id}: {str(e)}")
        
        return "Doctor rescheduled notifications sent successfully"

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.error(f"Error sending doctor rescheduled notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment rescheduled notification."


from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AppointmentNotifications

# REMINDER_FLAG_MAP = {
#     "one_week": "one_week_reminder_sent",
#     "three_days": "three_days_reminder_sent",
#     "one_day": "one_day_reminder_sent",
#     "one_hour": "one_hour_reminder_sent",
#     "on_time": "on_time_reminder_sent",
# }

# @shared_task(bind=True, autoretry_for=(), retry_backoff=False)
# def send_reminder(self, appointment_id, reminder_type):
#     """Send appointment reminders with proper error handling."""
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         appointment_notifications, created = AppointmentNotifications.objects.get_or_create(
#             appointment=appointment
#         )
#         flag = REMINDER_FLAG_MAP.get(reminder_type)


#         if appointment.appointment_status != "confirmed":
#             logger.info(f"Skipping reminder: appointment {appointment_id} not confirmed.")
#             return "Not confirmed"
#         if appointment.start_time < timezone.now():
#             logger.info(f"Skipping reminder: appointment {appointment_id} already started.")
#             return "Already started"
        
#         updated = AppointmentNotifications.objects.filter(
#             appointment_id=appointment_id,
#             **{flag: False}
#         ).update(**{flag: True})

#         if updated == 0:
#             logger.info(f"{reminder_type} already sent for {appointment_id}")
#             return

#         reminder_messages = {
#             "one_week": "Your consultation is in one week.",
#             "three_days": "Your consultation is in three days.",
#             "one_day": "Your consultation is in 24 hours.",
#             "one_hour": "Your consultation starts in one hour.",
#             "on_time": "Your consultation has started. Please join now.",
#         }

#         message = reminder_messages.get(reminder_type, "Appointment Reminder")

#         # EMAIL: Customer
#         try:
#             if appointment.customer.confirmation_method.lower() in ["email", "both"]:
#                 if reminder_type == "on_time":
#                     send_appointment_started_reminder_customer_email(appointment_id, message)
#                 else:
#                     send_appointment_reminder_customer_email(appointment_id, message)
#         except Exception as e:
#             logger.error(f"Email reminder failed for appointment {appointment_id}: {e}")

#         # WHATSAPP: Customer
#         try:
#             if appointment.customer.confirmation_method.lower() in ["whatsapp", "both"]:
#                 if reminder_type == "one_hour":
#                     send_wa_consultation_reminder_1_hour_before(appointment_id)
#                 else:
#                     send_wa_consultation_reminder_24_hours_before(appointment_id)
#         except Exception as e:
#             logger.error(f"WhatsApp reminder failed for appointment {appointment_id}: {e}")

#         # DOCTOR EMAIL
#         try:
#             if reminder_type == "on_time":
#                 send_appointment_started_reminder_doctor_email(appointment_id, message)
#             else:
#                 send_appointment_reminder_doctor_email(appointment_id, message)
#         except Exception as e:
#             logger.error(f"Doctor email reminder failed for appointment {appointment_id}: {e}")

#         # WHATSAPP: Doctor
#         try:
#             if reminder_type == "one_hour":
#                 send_wa_specialist_reminder_1_hour_before(appointment_id)
#             else:
#                 send_wa_specialist_reminder_1_hour_before(appointment_id)
#         except Exception as e:
#             logger.error(f"Doctor WhatsApp reminder failed for appointment {appointment_id}: {e}")

#         return f"Reminder task completed successfully for appointment {appointment_id}"

#     except AppointmentHeader.DoesNotExist:
#         logger.error(f"Appointment does not exist: {appointment_id}")
#         return "Appointment not found"

#     except Exception as e:
#         logger.exception(f"Unhandled error in send_reminder task for appointment {appointment_id}: {e}")
#         return f"Failed: {str(e)}"

# @shared_task
# def schedule_all_reminders(appointment_id):
#     """Schedule all reminders with proper error handling."""
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         notifications, created = AppointmentNotifications.objects.get_or_create(appointment=appointment)
#         if created or not notifications.appointment_reminders_scheduled:
#             notifications.appointment_reminders_scheduled = True
#             notifications.save()
#         else:
#             logger.info(f"Reminders already scheduled for appointment {appointment_id}")
#             return "Reminders already scheduled"
#         start_time = appointment.start_time
#         now = timezone.now()

#         reminder_offsets = [
#             ("one_week", timedelta(days=7)),
#             ("three_days", timedelta(days=3)),
#             ("one_day", timedelta(days=1)),
#             ("one_hour", timedelta(hours=1)),
#             ("on_time", timedelta(seconds=0)),
#         ]

#         for reminder_name, offset in reminder_offsets:
#             try:
#                 reminder_time = start_time - offset
#                 if reminder_time > now:
#                     send_reminder.apply_async(
#                         (appointment_id, reminder_name),
#                         eta=reminder_time
#                     )
#                     logger.info(f"Scheduled {reminder_name} reminder for appointment {appointment_id}")
#             except Exception as e:
#                 logger.error(f"Error scheduling {reminder_name} reminder for appointment {appointment_id}: {str(e)}")
        
#         return "All reminders scheduled successfully"
    
#     except AppointmentHeader.DoesNotExist:
#         logger.error(f"Appointment does not exist: {appointment_id}")
#         return "Appointment not found"
#     except Exception as e:
#         logger.error(f"Error in schedule_all_reminders for appointment {appointment_id}: {str(e)}")
#         return f"Error scheduling reminders: {str(e)}"



REMINDER_FLAG_MAP = {
    "one_week": "one_week_reminder_sent",
    "three_days": "three_days_reminder_sent",
    "one_day": "one_day_reminder_sent",
    "one_hour": "one_hour_reminder_sent",
    "on_time": "on_time_reminder_sent",
}

@shared_task(bind=True, autoretry_for=(), retry_backoff=False)
def send_reminder(self, appointment_id, reminder_type):

    logger.info("send_reminder task called")
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

        flag = REMINDER_FLAG_MAP.get(reminder_type)
        if not flag:
            logger.error(f"Invalid reminder_type '{reminder_type}' for appointment {appointment_id}")
            return "Invalid reminder type"

        if appointment.appointment_status != "confirmed":
            logger.info(f"Skipping reminder: appointment {appointment_id} not confirmed.")
            return "Not confirmed"

        if appointment.start_time < timezone.now():
            logger.info(f"Skipping reminder: appointment {appointment_id} already started.")
            return "Already started"



        from django.db import transaction

        with transaction.atomic():
            notif = (
                AppointmentNotifications.objects
                .select_for_update()
                .get(appointment_id=appointment_id)
            )

            if getattr(notif, flag):
                return "Already sent"

            setattr(notif, flag, True)
            notif.save()

        reminder_messages = {
            "one_week": "Your consultation is in one week.",
            "three_days": "Your consultation is in three days.",
            "one_day": "Your consultation is in 24 hours.",
            "one_hour": "Your consultation starts in one hour.",
            "on_time": "Your consultation has started. Please join now.",
        }

        message = reminder_messages.get(reminder_type, "Appointment Reminder")

        try:
            if appointment.customer.confirmation_method.lower() in ["email", "both"]:
                if reminder_type == "on_time":
                    send_appointment_started_reminder_customer_email(appointment_id)
                else:
                    send_appointment_reminder_customer_email(appointment_id, message)
        except Exception:
            logger.exception(f"Customer email reminder failed for {appointment_id}")

        try:
            if appointment.customer.confirmation_method.lower() in ["whatsapp", "both"]:
                if reminder_type == "one_hour":
                    send_wa_consultation_reminder_1_hour_before(appointment_id)
                else:
                    send_wa_consultation_reminder_24_hours_before(appointment_id)
        except Exception:
            logger.exception(f"Customer WhatsApp reminder failed for {appointment_id}")

        try:
            if reminder_type == "on_time":
                send_appointment_started_reminder_doctor_email(appointment_id)
            else:
                send_appointment_reminder_doctor_email(appointment_id, message)
        except Exception:
            logger.exception(f"Doctor email reminder failed for {appointment_id}")

        try:
            send_wa_specialist_reminder_1_hour_before(appointment_id)
        except Exception:
            logger.exception(f"Doctor WhatsApp reminder failed for {appointment_id}")

        return f"Reminder {reminder_type} completed for appointment {appointment_id}"

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist: {appointment_id}")
        return "Appointment not found"

    except Exception:
        logger.exception(f"Unhandled error in send_reminder for appointment {appointment_id}")
        return "Failed"

from django.db import transaction

@shared_task
def schedule_all_reminders(appointment_id):
    try:
        logger.info("schedule_all_reminders task called")
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

        with transaction.atomic():
            notifications, _ = AppointmentNotifications.objects.select_for_update().get_or_create(
                appointment=appointment
            )

            if notifications.appointment_reminders_scheduled:
                logger.info(f"Reminders already scheduled for {appointment_id}")
                return "Reminders already scheduled"

            notifications.appointment_reminders_scheduled = True
            notifications.save(update_fields=["appointment_reminders_scheduled"])

        start_time = appointment.start_time
        now = timezone.now()

        reminder_offsets = [
            ("one_week", timedelta(days=7)),
            ("three_days", timedelta(days=3)),
            ("one_day", timedelta(days=1)),
            ("one_hour", timedelta(hours=1)),
            ("on_time", timedelta(minutes=1)),  
        ]

        # for reminder_name, offset in reminder_offsets:
        #     logger.debug(f"Scheduling {reminder_name} for appointment {appointment_id}")
        #     reminder_time = start_time - offset
        #     if reminder_time > now:
        #         task = send_reminder.apply_async(
        #             (appointment_id, reminder_name),
        #             eta=reminder_time
        #         )
        #         logger.info(
        #             f"Scheduled {reminder_name} for appointment {appointment_id}, task_id={task.id}"
        #         )


        for reminder_name, offset in reminder_offsets:
            logger.debug(f"Scheduling {reminder_name} for appointment {appointment_id}")
            reminder_time = start_time - offset
            if reminder_time > now:
                task = send_reminder.apply_async(
                    (appointment_id, reminder_name),
                    eta=now
                )
                logger.info(
                    f"Scheduled {reminder_name} for appointment {appointment_id}, task_id={task.id} , at {reminder_time}"
                )


        # task = send_reminder.apply_async(
        #         (appointment_id, "one_hour"),
        #         eta=now
        #     )
        # logger.info(
        #     f"Scheduled one_hour for appointment {appointment_id}, task_id={task.id}"
        # )


        return "All reminders scheduled successfully"

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist: {appointment_id}")
        return "Appointment not found"

    except Exception as e:
        logger.exception(f"Error scheduling reminders for appointment {appointment_id}")
        return str(e)

from .models import Reminder_Sent_History
from analysis.models import Meeting_Tracker
from analysis.models import AppointmentHeader


@shared_task
def monitor_appointment(appointment_id):
    """Monitor appointment attendance with proper error handling."""
    logger.debug(appointment_id)
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        tracker = Meeting_Tracker.objects.get(appointment=appointment)
    except Meeting_Tracker.DoesNotExist:
        logger.error(f'Meeting Tracker does not exist for appointment {appointment_id}')
        return 'Meeting Tracker does not exist'
    except AppointmentHeader.DoesNotExist:
        logger.error(f'Appointment does not exist: {appointment_id}')
        return 'Appointment does not exist'
    except Exception as e:
        logger.error(f'Error retrieving appointment/tracker for {appointment_id}: {str(e)}')
        return f'Error: {str(e)}'
    
    # Doctor monitoring
    if not tracker.doctor_joined:
        if appointment.start_time + timedelta(minutes=15) < timezone.now():
            # Doctor missed - send notifications
            try:
                send_appointment_missed_email(
                    to_email=tracker.appointment.doctor.email_id,
                    patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    appointment_id=tracker.appointment.appointment_id,
                    doctor_flag=1,
                )
            except Exception as e:
                logger.error(f"Error sending missed email to doctor for appointment {appointment_id}: {str(e)}")
            
            try:
                send_doctor_missed_to_customer_email(
                    to_email=tracker.customer_1.email,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                )
            except Exception as e:
                logger.error(f"Error sending doctor missed email to customer1 for appointment {appointment_id}: {str(e)}")
            
            if tracker.customer_2:
                try:
                    send_doctor_missed_to_customer_email(
                        to_email=tracker.customer_2.email,
                        doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                        doctor_salutation=tracker.appointment.doctor.salutation,
                        patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                        appointment_id=tracker.appointment.appointment_id,
                    )
                except Exception as e:
                    logger.error(f"Error sending doctor missed email to customer2 for appointment {appointment_id}: {str(e)}")
            
            appointment.appointment_status = 'doctor_missed'
            appointment.save()
        else:
            # Send reminder to doctor
            try:
                send_appointment_started_reminder_doctor_email(
                    to_email=tracker.appointment.doctor.email_id,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_1_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    patient_2_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name if tracker.customer_2 else '',
                    date=tracker.appointment.start_time.date().strftime("%B %d, %Y"),
                    weekday=tracker.appointment.start_time.date().strftime("%A"),
                    time=tracker.appointment.start_time.time().strftime("%I:%M %p"),
                    specialization=tracker.appointment.specialization,
                    meeting_link=tracker.meeting_link,
                )
                
                Reminder_Sent_History.objects.create(
                    user=tracker.appointment.doctor,
                    user_is_customer=False,
                    appointment=tracker.appointment,
                    email=tracker.appointment.doctor.email_id,
                    subject='Appointment Started Reminder',
                    body=f'Your appointment with {tracker.customer_1.user.first_name} {tracker.customer_1.user.last_name} has started.',
                )
            except Exception as e:
                logger.error(f"Error sending started reminder to doctor for appointment {appointment_id}: {str(e)}")
    
    # Customer 1 monitoring
    if not tracker.customer_1_joined:
        if appointment.start_time + timedelta(minutes=15) < timezone.now():
            # Customer 1 missed
            try:
                send_appointment_missed_email(
                    to_email=tracker.customer_1.email,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                    doctor_flag=0,
                )
            except Exception as e:
                logger.error(f"Error sending missed email to customer1 for appointment {appointment_id}: {str(e)}")
            
            try:
                send_patient_missed_to_doctor_email(
                    to_email=tracker.appointment.doctor.email_id,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_1.user.first_name + ' ' + tracker.customer_1.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                )
            except Exception as e:
                logger.error(f"Error sending customer1 missed email to doctor for appointment {appointment_id}: {str(e)}")
            
            appointment.appointment_status = 'customer_missed'
            appointment.save()
        else:
            # Send reminder to customer 1
            try:
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
                    body=f'Your appointment with {tracker.doctor.first_name} {tracker.doctor.last_name} has started.',
                )
            except Exception as e:
                logger.error(f"Error sending started reminder to customer1 for appointment {appointment_id}: {str(e)}")
    
    # Customer 2 monitoring
    if tracker.customer_2 and not tracker.customer_2_joined:
        if appointment.start_time + timedelta(minutes=15) < timezone.now():
            # Customer 2 missed
            try:
                send_appointment_missed_email(
                    to_email=tracker.customer_2.email,
                    doctor_name=tracker.doctor.first_name + ' ' + tracker.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                    doctor_flag=0,
                )
            except Exception as e:
                logger.error(f"Error sending missed email to customer2 for appointment {appointment_id}: {str(e)}")
            
            try:
                send_patient_missed_to_doctor_email(
                    to_email=tracker.appointment.doctor.email_id,
                    doctor_name=tracker.appointment.doctor.first_name + ' ' + tracker.appointment.doctor.last_name,
                    doctor_salutation=tracker.appointment.doctor.salutation,
                    patient_name=tracker.customer_2.user.first_name + ' ' + tracker.customer_2.user.last_name,
                    appointment_id=tracker.appointment.appointment_id,
                )
            except Exception as e:
                logger.error(f"Error sending customer2 missed email to doctor for appointment {appointment_id}: {str(e)}")
            
            appointment.appointment_status = 'customer_missed'
            appointment.save()
        else:
            # Send reminder to customer 2
            try:
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
                
                Reminder_Sent_History.objects.create(
                    user=tracker.customer_2.user,
                    user_is_customer=True,
                    appointment=tracker.appointment,
                    email=tracker.customer_2.user.email,
                    subject='Appointment Started Reminder',
                    body=f'Your appointment with {tracker.doctor.first_name} {tracker.doctor.last_name} has started.',
                )
            except Exception as e:
                logger.error(f"Error sending started reminder to customer2 for appointment {appointment_id}: {str(e)}")

    if appointment.start_time + timedelta(minutes=15) < timezone.now():
        return 'Appointment monitoring completed'


@shared_task
def send_payment_pending_notification(appointment_id):
    """
    Send payment pending notifications with proper recursion control.
    Sends reminders at 47 hours and 24 hours before appointment.
    """
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        
        # Get or create notification tracker to prevent duplicate sends
        from .models import AppointmentNotifications
        appointment_notifications, created = AppointmentNotifications.objects.get_or_create(
            appointment=appointment
        )
        
        # Calculate time until appointment
        time_until_appointment = appointment.start_time - timezone.now()
        
        # Check if payment is already done - exit early
        if appointment.payment_done:
            logger.info(f'Payment already completed for appointment {appointment_id}')
            return "Payment already completed"
        
        # Check if appointment is cancelled or completed - exit early
        if appointment.appointment_status in ['cancelled', 'completed', 'doctor_missed', 'customer_missed']:
            logger.info(f'Appointment {appointment_id} status is {appointment.appointment_status}, stopping payment reminders')
            return f"Appointment status: {appointment.appointment_status}"
        
        # First reminder: 47+ hours before appointment
        if time_until_appointment > timedelta(hours=47):
            # Only send if not already sent
            if not appointment_notifications.payment_reminder_47h_sent:
                # Send email reminder
                try:
                    if appointment.customer.confirmation_method in ["email", "Email", "both"]:
                        send_payment_pending_email(appointment_id)
                        logger.info(f'Sent 47h payment reminder email for appointment {appointment_id}')
                except Exception as e:
                    logger.error(f"Error sending 47h payment reminder email for appointment {appointment_id}: {str(e)}")
                
                # Send WhatsApp reminder
                try:
                    if appointment.customer.confirmation_method in ["whatsapp", "WhatsApp", "both"]:
                        send_wa_payment_pending_reminder(appointment_id)
                        logger.info(f'Sent 47h payment reminder WhatsApp for appointment {appointment_id}')
                except Exception as e:
                    logger.error(f"Error sending 47h payment reminder WhatsApp for appointment {appointment_id}: {str(e)}")
                
                # Mark as sent
                appointment_notifications.payment_reminder_47h_sent = True
                appointment_notifications.save()
                
                # Schedule the 24-hour reminder
                time_to_24h_reminder = time_until_appointment - timedelta(hours=24)
                countdown_seconds = int(time_to_24h_reminder.total_seconds())
                
                if countdown_seconds > 0:
                    try:
                        send_payment_pending_notification.apply_async(
                            (appointment.appointment_id,), 
                            countdown=countdown_seconds
                        )
                        logger.info(f'Scheduled 24h payment reminder for appointment {appointment_id} in {countdown_seconds} seconds')
                    except Exception as e:
                        logger.error(f"Error scheduling 24h payment reminder for appointment {appointment_id}: {str(e)}")
            else:
                logger.info(f'47h payment reminder already sent for appointment {appointment_id}')
        
        # Final reminder: 24-47 hours before appointment
        elif timedelta(hours=24) < time_until_appointment <= timedelta(hours=47):
            # Only send if not already sent
            if not appointment_notifications.payment_reminder_24h_sent:
                # Send email reminder
                try:
                    if appointment.customer.confirmation_method in ["email", "Email", "both"]:
                        send_payment_pending_email_final(appointment_id)
                        logger.info(f'Sent 24h final payment reminder email for appointment {appointment_id}')
                except Exception as e:
                    logger.error(f"Error sending 24h payment reminder email for appointment {appointment_id}: {str(e)}")
                
                # Send WhatsApp reminder
                try:
                    if appointment.customer.confirmation_method in ["whatsapp", "WhatsApp", "both"]:
                        send_wa__final_payment_reminder_24_hours_before_consultation_time(appointment_id)
                        logger.info(f'Sent 24h final payment reminder WhatsApp for appointment {appointment_id}')
                except Exception as e:
                    logger.error(f"Error sending 24h payment reminder WhatsApp for appointment {appointment_id}: {str(e)}")
                
                # Mark as sent - THIS IS THE FINAL REMINDER
                appointment_notifications.payment_reminder_24h_sent = True
                appointment_notifications.save()
                
                logger.info(f'Final payment reminder sent for appointment {appointment_id}, no more reminders will be sent')
        
        # Too close to appointment time (less than 24 hours)
        else:
            logger.warning(f'Appointment {appointment_id} is less than 24 hours away, payment reminder not sent')
            return "Too close to appointment time"
        
        return "Payment reminder processed successfully"
        
    except AppointmentHeader.DoesNotExist:
        logger.error(f'Appointment with ID {appointment_id} does not exist')
        return f'Appointment {appointment_id} does not exist'
    
    except Exception as e:
        logger.error(f'Error in send_payment_pending_notification for appointment {appointment_id}: {e}')
        return f'Error: {str(e)}'


from analysis.models import Referral, Referral_customer, AppointmentHeader


@shared_task
def schedule_reminder_to_book_appointment(appointment_id=None, referral_id=None):
    """Schedule reminders to book appointments with proper error handling."""
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
        logger.error(f'Appointment with ID {appointment_id} does not exist')
        return f'Appointment with ID {appointment_id} does not exist'
    except Referral.DoesNotExist:
        logger.error(f'Referral with ID {referral_id} does not exist')
        return f'Referral with ID {referral_id} does not exist'
    except Exception as e:
        logger.error(f'Error retrieving data: {str(e)}')
        return f'Error retrieving data: {str(e)}'
   
    # Handle appointment logic
    if appointment and (appointment.appointment_status != 'confirmed' or "cancelled" not in appointment.appointment_status):
        # Email reminders
        try:
            if appointment.customer.confirmation_method in ["email", "Email", "both"]:
                if appointment.start_time - timedelta(hours=47) > timezone.now():
                    send_followup_referal_reminder_email(
                        to_email=appointment.customer.email,
                        name=appointment.customer.user.first_name + ' ' + appointment.customer.user.last_name,
                        specialization=appointment.specialization.specialization,
                        doctor_name=appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
                        doctor_salutation=appointment.doctor.salutation,
                    )
                    logger.info(f'Sent 47h booking reminder email for appointment {appointment_id}')
                    
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
                        subject='Appointment not scheduled Reminder final',
                        body=f'You have not scheduled your consultation with {appointment.doctor.first_name} {appointment.doctor.last_name} | {appointment.specialization.specialization}. Please schedule your consultation as soon as possible.',
                    )
                    logger.info(f'Sent 24h final booking reminder email for appointment {appointment_id}')
        except Exception as e:
            logger.error(f"Error sending booking reminder email for appointment {appointment_id}: {str(e)}")

        # WhatsApp reminders
        try:
            if appointment.customer.confirmation_method in ["WhatsApp", "whatsapp", "both"]:
                if appointment.start_time - timedelta(hours=47) > timezone.now():
                    send_wa_consultation_reminder_not_yet_scheduled(appointment)
                    logger.info(f'Sent 47h booking reminder WhatsApp for appointment {appointment_id}')
                    
                elif appointment.start_time - timedelta(hours=24) > timezone.now():
                    send_wa_final_consultation_reminder_not_yet_scheduled(
                        patient_name=f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}",
                        salutation=appointment.doctor.salutation,
                        specialist_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                        to_phone=f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
                    )
                    logger.info(f'Sent 24h final booking reminder WhatsApp for appointment {appointment_id}')
        except Exception as e:
            logger.error(f"Error sending booking reminder WhatsApp for appointment {appointment_id}: {str(e)}")
    
    # Handle referral logic
    elif referral and not referral.converted_to_appointment:
        for customer in referal_customers:
            # Email reminders
            try:
                if customer.customer.confirmation_method in ["email", "Email", "both"]:
                    send_followup_referal_reminder_email(
                        to_email=customer.customer.email,
                        name=customer.customer.user.first_name + ' ' + customer.customer.user.last_name,
                        specialization=referral.specialization.specialization,
                        doctor_name=referral.doctor.first_name + ' ' + referral.doctor.last_name,
                        doctor_salutation=referral.doctor.salutation,
                    )
                    logger.info(f'Sent referral booking reminder email for referral {referral_id}')
            except Exception as e:
                logger.error(f"Error sending referral booking reminder email for referral {referral_id}: {str(e)}")
            
            # WhatsApp reminders
            try:
                if customer.customer.confirmation_method in ["WhatsApp", "whatsapp", "both"]:
                    send_wa_consultation_reminder_not_yet_scheduled(
                        patient_name=f"{customer.customer.user.first_name} {customer.customer.user.last_name}",
                        salutation=referral.doctor.salutation,
                        specialist_name=f"{referral.doctor.first_name} {referral.doctor.last_name}",
                        to_phone=f"{customer.customer.country_code}{customer.customer.whatsapp_number}"
                    )
                    logger.info(f'Sent referral booking reminder WhatsApp for referral {referral_id}')
            except Exception as e:
                logger.error(f"Error sending referral booking reminder WhatsApp for referral {referral_id}: {str(e)}")
    
    return "Booking reminder processed successfully"


@shared_task
def send_doctor_replied_to_patient_notifiaction(to_phone, name, specialist_name):
    """Send doctor reply notification with proper error handling."""
    try:
        logger.debug(send_wa_specialist_reply_notification_to_patient(to_phone, name, specialist_name))
        return "Doctor reply notification sent successfully"
    except Exception as e:
        logger.error(f"Error sending doctor reply notification: {str(e)}")
        return f"Error sending doctor reply notification: {str(e)}"