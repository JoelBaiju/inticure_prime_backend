from general.smss import appointmentbooked
from general.tasks import send_appointment_confirmation_customer_email_task
from analysis.models import Meeting_Tracker


class NotificationService:
    @staticmethod
    def send_appointment_confirmation(appointment):
        """Send appointment confirmation via SMS or Email"""
        try:
            meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        except Meeting_Tracker.DoesNotExist:
            meeting_tracker = None

        if appointment.confirmation_method == "SMS":
            appointmentbooked(appointment.appointment_id)
        elif appointment.confirmation_method == "Email":
            NotificationService._send_email_confirmation(appointment, meeting_tracker)

    @staticmethod
    def _send_email_confirmation(appointment, meeting_tracker):
        """Send email confirmation for appointment"""
        customer_meeting_link = meeting_tracker.customer_meeting_link if meeting_tracker else ""
        
        send_appointment_confirmation_customer_email_task.delay(appointment.appointment_id)