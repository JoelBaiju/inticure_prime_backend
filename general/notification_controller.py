
from .emal_service import *
from whatsapp.whatsapp_messages import *
from analysis.models import AppointmentHeader

def send_appointment_cancel_notification(appointment_id):

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment.appointment_id)
        if appointment.customer.confirmation_method == 'email':
            send_appointment_cancellation_email(appointment_id)
        if appointment.customer.confirmation_method == 'whatsapp':
            send_wa_patient_requested_cancellation(to_phone=appointment.customer.whatsapp_number,
                                                 patient_name=appointment.customer.first_name,
                                                 salutation=appointment.doctor.salutation,
                                                 specialist_name=appointment.doctor.last_name,
                                                 date_time=appointment.start_time.strftime("%Y-%m-%d %I:%M %p"))

        send_appointment_cancellation_email_to_specialist(appointment_id)
        send_wa_consultation_canceled_by_patient_to_specialist(appointment)

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment.appointment_id}")
        return "Appointment does not exist."