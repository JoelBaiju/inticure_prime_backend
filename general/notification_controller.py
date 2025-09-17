
from .emal_service import *
from whatsapp.whatsapp_messages import *
from analysis.models import AppointmentHeader

def send_appointment_cancel_notification(appointment_id):

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment.appointment_id)
        if appointment.customer.confirmation_method == 'email':
            send_appointment_cancellation_email(appointment_id)
        if appointment.customer.confirmation_method == 'whatsapp':
            send_wa_patient_requested_cancellation(appointment_id)

        send_appointment_cancellation_email_to_specialist(appointment_id)
        send_wa_consultation_canceled_by_patient_to_specialist(appointment_id)

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment.appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        print(f"Error sending appointment cancel notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment cancel notification."




def send_appointment_confirmation_notification(appointment_id):
    
    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        if appointment.customer.confirmation_method == 'email':
            send_appointment_confirmation_customer_email(appointment_id)
            send_first_appointment_confirmation_email(appointment_id)
            send_appointment_confirmation_doctor_email(appointment_id)
        if appointment.customer.confirmation_method == 'whatsapp':
            send_wa_consultation_confirmation_to_specialist(appointment_id)
            send_wa_appointment_confirmation(appointment_id)
            send_wa_first_consultation_confirmation(appointment_id)

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        print(f"Error sending appointment confirmation notification for appointment id {appointment_id}: {str(e)}")
        return "Error sending appointment confirmation notification."