from celery import shared_task
from .models import AppointmentHeader
from doctor.models import DoctorAppointment
from general.tasks import send_payment_pending_email_task

@shared_task
def delete_unpaid_appointment(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        if not appointment.payment_done:
            DoctorAppointment.objects.filter(appointment=appointment).delete()
            # appointment.delete()
            # send_payment_pending_email_task.delay(appointment_id=appointment.appointment_id)
            
            return f"Deleted unpaid appointment {appointment_id}"
        return f"Appointment {appointment_id} was paid, not deleted."
    except AppointmentHeader.DoesNotExist:
        return f"Appointment {appointment_id} not found."



