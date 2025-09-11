from datetime import timedelta
from django.utils import timezone
from analysis.models import Reschedule_history
from doctor.models import DoctorProfiles,DoctorAppointment
from general.utils import is_doctor_available           

class AppointmentValidator:
    @staticmethod
    def validate_reschedule_eligibility(appointment):
        """Validate if appointment can be rescheduled"""
        if appointment.appointment_status in ['completed', 'cancelled', 'rescheduled_by_doctor', "rescheduled_by_customer"]:
            raise ValueError("Cannot reschedule a completed, cancelled, or already rescheduled appointment.")
        
        if appointment.start_time < timezone.now() - timedelta(hours=6):
            raise ValueError("Reschedule only allowed 6 hours before appointment.")
            
        if appointment.start_time < timezone.now():
            raise ValueError("Appointment date is past. Reschedule not allowed.")

        if Reschedule_history.objects.filter(appointment=appointment).exists():
            raise ValueError("You have reached the maximum number of reschedules allowed.")

    @staticmethod
    def validate_reschedule_status(appointment):
        """Validate appointment is in correct status for reschedule completion"""
        if appointment.appointment_status not in ['rescheduled_by_customer', 'rescheduled_by_doctor']:
            raise ValueError("Reschedule not initiated.")
            
        if appointment.appointment_status in ['completed', 'cancelled']:
            raise ValueError("Appointment already completed or cancelled.")

    @staticmethod
    def validate_cancellation_eligibility(appointment):
        """Validate if appointment can be cancelled"""
        reschedule_history = Reschedule_history.objects.filter(appointment=appointment).exists()
        
        if reschedule_history:
            raise ValueError("You cannot cancel an already rescheduled appointment.")
            
        if appointment.appointment_status == 'cancelled_by_customer':
            raise ValueError("Appointment already cancelled by customer.")
            
        if appointment.appointment_status == 'completed':
            raise ValueError("Appointment already completed.")

        if not appointment.start_time - timedelta(hours=24) > timezone.now():
            raise ValueError("Cancellation is only allowed before 24 hours.")
            
        if appointment.start_time.date() == timezone.now().date():
            raise ValueError("Appointment date is today. Cancellation not allowed.")
            
        if appointment.start_time.date() < timezone.now().date():
            raise ValueError("Appointment date is past. Cancellation not allowed.")

    @staticmethod
    def validate_appointment_timing(start_time, hours_before=6):
        """Validate if appointment can be modified based on timing"""
        current_time = timezone.now()
        
        if start_time < current_time:
            raise ValueError("Appointment date is in the past.")
            
        if start_time < current_time + timedelta(hours=hours_before):
            raise ValueError(f"Modification only allowed {hours_before} hours before appointment.")

    @staticmethod
    def validate_slot_availability(doctor, start_time, end_time):
        """Check if doctor slot is available for booking"""
        from doctor.models import DoctorAppointment
        
        overlapping = DoctorAppointment.objects.filter(
            doctor=doctor,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if overlapping:
            raise ValueError("Doctor is not available at this time. Slot already booked.")


    @staticmethod
    def does_appointment_slot_exist(appointment):
        current_start_time = appointment.start_time
        current_end_time = appointment.end_time
        slot_exists = False
        try:
            doctor_appointments = DoctorAppointment.objects.filter(
                appointment=appointment
            )
            if doctor_appointments.exists():
                slot_exists = True
        except DoctorAppointment.DoesNotExist:
            slot_exists = False

        if not slot_exists:
            
            slot_exists = is_doctor_available(
                doctor_id=appointment.doctor,
                from_time=current_start_time,
                to_time=current_end_time
            )
             
        return slot_exists


class ProfileValidator:
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate required fields in request data"""
        missing_fields = []
        
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    @staticmethod
    def validate_partner_creation_data(data):
        """Validate partner creation data"""
        required_fields = ['first_name', 'last_name', 'country', 'gender', 'dob']
        ProfileValidator.validate_required_fields(data, required_fields)
        
        # Additional validation can be added here
        if data.get('email') and not ProfileValidator._is_valid_email(data['email']):
            raise ValueError("Invalid email format.")

    @staticmethod
    def _is_valid_email(email):
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None