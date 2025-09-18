from datetime import timedelta
from django.utils import timezone
from celery import current_app

from analysis.models import AppointmentHeader, Reschedule_history, Cancel_history,Meeting_Tracker
from doctor.models import DoctorAppointment
from general.models import PreTransactionData
from customer.models import Refund
from general.utils import (
    get_customer_timezone, convert_local_dt_to_utc, 
    convert_local_dt_to_utc_return_dt, is_doctor_available,
    track_map_meeting
)
from general.gmeet.gmeet import generate_google_meet
from general.tasks import send_appointment_rescheduled_email_task, send_appointment_cancellation_email_task
from doctor.slots_service import get_available_slots
from customer.utils.validators import AppointmentValidator
from analysis.views import ConfirmAppointment

from general.notification_controller import send_appointment_reshceduled_notification

class AppointmentService:
    @staticmethod
    def find_next_available_slot(doctor_id, available_dates, timezone_str, is_couple):
        """Find next available slot from available dates"""
        for next_date in available_dates:
            try:
                next_dt_start = convert_local_dt_to_utc(f"{next_date}T00:00:00", timezone_str)
                next_dt_end = convert_local_dt_to_utc(f"{next_date}T23:59:59", timezone_str)
            except ValueError:
                continue
                
            next_results = get_available_slots(
                doctor_id=doctor_id,
                date_time_start=next_dt_start,
                date_time_end=next_dt_end,
                is_couple=is_couple,
                timezone_str=timezone_str
            )
            
            next_slots = next_results.get('slots', [])
            if next_slots:
                next_results['current_date'] = str(next_dt_start.date())
                return next_results
                
        return {"slots": [], "current_date": str(next_dt_start.date())}

    @staticmethod
    def initiate_reschedule(appointment, reason):
        """Initiate appointment reschedule process"""
        appointment.appointment_status = 'rescheduled_by_customer'
        appointment.meeting_link = ''
        appointment.save()
        
        Reschedule_history.objects.create(
            appointment=appointment, 
            reason=reason, 
            initiated_by='customer'
        )

    @staticmethod
    def complete_reschedule(appointment, slot_data, user, is_admin=False):
        """Complete appointment reschedule with new slot"""
        date_str = slot_data.get('date')
        start_str = slot_data.get('start')
        end_str = slot_data.get('end')
        if is_admin:
            time_zone = 'Asia/Calcutta'
        else:
            time_zone = get_customer_timezone(user)
        start_datetime_utc = convert_local_dt_to_utc(start_str, time_zone)
        end_datetime_utc = convert_local_dt_to_utc(end_str, time_zone)

        # Check for overlapping appointments
        overlapping = DoctorAppointment.objects.filter(
            doctor=appointment.doctor,
            start_time__lt=end_datetime_utc,
            end_time__gt=start_datetime_utc
        ).exists()

        print("overlapping",overlapping)
        
        if overlapping:
            raise ValueError("Doctor is not available at this time. Slot already booked")

        # Delete old appointment and create new one
        DoctorAppointment.objects.filter(appointment=appointment, confirmed=True).delete()
        
        DoctorAppointment.objects.create(
            doctor=appointment.doctor,
            specialization=appointment.specialization,
            start_time=start_datetime_utc,
            end_time=end_datetime_utc,
            appointment=appointment,
            confirmed=True
        )

        # Update appointment with new meeting details
        appointment.appointment_status = 'confirmed'
        meeting_creds = generate_google_meet(
            summary='Appointment',
            description='Appointment with doctor',
            start_time=start_datetime_utc,
            end_time=end_datetime_utc
        )
        
        appointment.meeting_link = meeting_creds.get('meeting_link', '')
        meeting_tracker = track_map_meeting(
            appointment.appointment_id,
            appointment.meeting_link,
            meeting_creds.get('meeting_code', '')
        )

        # Send notification
        # send_appointment_rescheduled_email_task.delay(
        #     appointment_id=appointment.appointment_id,
        #     previous_date=appointment.start_time.date().strftime('%Y-%m-%d'),
        #     previous_time=appointment.start_time.time().strftime('%H:%M:%S'),
        #     new_date=start_datetime_utc.date().strftime('%Y-%m-%d'),
        #     new_time=start_datetime_utc.time().strftime('%H:%M:%S')
        # )
        
        send_appointment_reshceduled_notification.delay(
            appointment_id = appointment.appointment_id,
            old_date_time = appointment.start_time,
            new_date_time = start_datetime_utc          
        )

        appointment.end_time = end_datetime_utc
        appointment.start_time = start_datetime_utc
        appointment.save()

    @staticmethod
    def cancel_appointment(appointment, reason, is_admin=False):
        """Cancel appointment and handle refund"""
       
        # Delete doctor appointment and update status
        
        appointment.appointment_status = 'cancelled_by_customer'
        if is_admin:
            appointment.appointment_status = 'cancelled_by_admin'
        # Handle referral if exists
        if appointment.referral and appointment.referral.converted_to_appointment:
            appointment.referral.converted_to_appointment = False
            appointment.referral.save()
            
        appointment.save()

        # Create cancellation history
        Cancel_history.objects.create(appointment=appointment, reason=reason)

        # Calculate and create refund
        if not appointment.package_used:
            transaction = PreTransactionData.objects.filter(appointment=appointment).first()
            if transaction:
                refund_amount = AppointmentService._calculate_refund_amount(appointment, transaction)
                Refund.objects.create(
                    appointment=appointment,
                    refund_amount=refund_amount,
                    refund_currency=transaction.currency,
                    refund_status='pending',
                    request_date=timezone.now()
                )

        # Send cancellation notification
        send_appointment_cancellation_email_task.delay(appointment_id=appointment.appointment_id)
        
        # Revoke background tasks
        try:
            doctor_appointment = DoctorAppointment.objects.get(appointment=appointment)
            meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
            doctor_appointment.delete()
            if meeting_tracker.monitor_task_id:
                current_app.control.revoke(meeting_tracker.monitor_task_id, terminate=True)
            if meeting_tracker.reminder_task_id:
                current_app.control.revoke(meeting_tracker.reminder_task_id, terminate=True)

        except (DoctorAppointment.DoesNotExist, Meeting_Tracker.DoesNotExist):
            pass
     
    @staticmethod
    def _calculate_refund_amount(appointment, transaction):
        """Calculate refund amount based on cancellation timing"""
        if timezone.now() < appointment.start_time - timedelta(hours=72):
            return float(transaction.total_amount)
        else:
            return float(transaction.total_amount) / 2

    @staticmethod
    def     book_appointment_slot(appointment, slot_data, customer , is_admin=False):
        """-/*Book appointment slot for customer"""
        if DoctorAppointment.objects.filter(appointment=appointment).exists():
            raise ValueError("Slot already booked.")

        if is_admin:
            time_zone = 'Asia/Calcutta'
        else:
            time_zone = get_customer_timezone(customer.user)

        start_str = slot_data.get('start')
        end_str = slot_data.get('end')

        start_datetime_utc = convert_local_dt_to_utc_return_dt(start_str, customer.time_zone)
        end_datetime_utc = convert_local_dt_to_utc_return_dt(end_str, customer.time_zone)
        
        date = start_datetime_utc.date()
        
        # Check doctor availability
        doctor_available = is_doctor_available(
            doctor_id=appointment.doctor,
            # date_obj=date,
            from_time=start_datetime_utc,
            to_time=end_datetime_utc
        )
        
        if not doctor_available:
            raise ValueError("Doctor is not available at this time. Please select another slot.")

        # Create doctor appointment
        DoctorAppointment.objects.create(
            doctor=appointment.doctor,
            specialization=appointment.specialization,
            start_time=start_datetime_utc,
            end_time=end_datetime_utc,
            appointment=appointment,
            confirmed=True
        )

        # Update appointment details
        if appointment.payment_done:
            appointment.appointment_status = 'confirmed'
            
            meeting_creds = generate_google_meet(
                summary='Appointment',
                description='Appointment with doctor',
                start_time=start_datetime_utc,
                end_time=end_datetime_utc
            )
            
            appointment.meeting_link = meeting_creds.get('meeting_link', '')
            track_map_meeting(
                appointment.appointment_id,
                appointment.meeting_link,
                meeting_creds.get('meeting_code', '')
            )
        else:
            appointment.appointment_status = "pending_payment"

        appointment.appointment_date = date
        appointment.appointment_time = start_datetime_utc
        appointment.end_time = end_datetime_utc
        appointment.start_time = start_datetime_utc
        appointment.save()



    @staticmethod
    def relieve_appointment_package(appointment_id):
        """Remove package from appointment"""
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            raise AppointmentHeader.DoesNotExist("Appointment not found")
            
        if appointment.appointment_status == 'confirmed':
            raise ValueError('Appointment already confirmed')
        
        if appointment.package_included:
            appointment.package_included = False
            appointment.package = None
            appointment.save()
            
        return appointment


    @staticmethod
    def confirm_appointment(appointment):
        """Confirm appointment slot"""
        
        if not AppointmentValidator.does_appointment_slot_exist(appointment):
            return False

        ConfirmAppointment(appointment_id = appointment.appointment_id ,pretransaction_id=None, is_admin = True)
        appointment = AppointmentHeader.objects.get(appointment_id = appointment.appointment_id)
        appointment.confirmed_by_admin = True
        print("outsideeee",appointment.appointment_status)
        appointment.save()
        
        return True




    @staticmethod
    def complete_appointment(appointment):

        if appointment.appointment_status == 'completed':
            raise ValueError("Appointment already completed")
        appointment.appointment_status = 'completed'
        appointment.save()
        return True










