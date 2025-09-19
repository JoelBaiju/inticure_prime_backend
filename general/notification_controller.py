
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
        print(f"Appointment does not exist.for id {appointment.appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        print(f"Error sending appointment cancel notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment cancel notification."



@shared_task
def send_appointment_confirmation_notification(appointment_id):
    print(f"send_appointment_confirmation_notification for appointment id {appointment_id}")
    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        print(appointment.customer.confirmation_method)
        if appointment.customer.confirmation_method in  ['email' ,"Email" , "both" ]:
            print(f"send_appointment_confirmation_notification for appointment id {appointment_id} email")
            if appointment.customer.completed_first_analysis:
                send_appointment_confirmation_customer_email(appointment_id)
            else : 
                send_first_appointment_confirmation_email(appointment_id)
    
    
        if appointment.customer.confirmation_method in  ['whatsapp' ,"WhatsApp" , "both"]:
            print(f"send_appointment_confirmation_notification for appointment id {appointment_id} whatsapp")
            if appointment.customer.completed_first_analysis:
                send_wa_appointment_confirmation(appointment_id)
            else:
                send_wa_first_consultation_confirmation(appointment_id)

        send_wa_consultation_confirmation_to_specialist(appointment_id)
        send_appointment_confirmation_doctor_email(appointment_id)

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        print(f"Error sending appointment confirmation notification for appointment id {appointment_id}: {str(e)}")
        return f"Error sending appointment confirmation notification.{e}"
    


@shared_task
def send_appointment_reshceduled_notification(appointment_id,old_date_time , new_date_time):
    print(f"send_appointment_reshceduled_notification for appointment id {appointment_id}")

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
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        print(f"Error sending appointment rescheduled notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment rescheduled notification."
    



# @shared_task
# def send_appointment_reminders(appointment_id):