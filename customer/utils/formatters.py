from datetime import datetime
from django.utils import timezone
from general.utils import get_customer_timezone


class TimeZoneFormatter:
    @staticmethod
    def convert_to_customer_timezone(datetime_obj, customer):
        """Convert UTC datetime to customer's timezone"""
        customer_tz = get_customer_timezone(customer.user)
        if customer_tz:
            # Implementation depends on your timezone utility functions
            pass
        return datetime_obj

    @staticmethod
    def format_appointment_times(appointment):
        """Format appointment times for display"""
        return {
            'start_time': appointment.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': appointment.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': appointment.start_time.date().strftime('%Y-%m-%d'),
            'time': appointment.start_time.time().strftime('%H:%M')
        }

    @staticmethod
    def format_datetime_for_display(dt, format_str='%Y-%m-%d %H:%M'):
        """Format datetime for user display"""
        if not dt:
            return None
        return dt.strftime(format_str)


class ResponseFormatter:
    @staticmethod
    def success_response(data=None, message="Success"):
        """Standard success response format"""
        response_data = {
            "success": True,
            "message": message
        }
        if data is not None:
            response_data["data"] = data
        return response_data

    @staticmethod
    def error_response(message, error_code=None):
        """Standard error response format"""
        response_data = {
            "success": False,
            "error": message
        }
        if error_code:
            response_data["error_code"] = error_code
        return response_data

    @staticmethod
    def paginated_response(items, page=1, total_pages=1, total_items=0):
        """Standard paginated response format"""
        return {
            "success": True,
            "data": items,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items
            }
        }


class PrescriptionFormatter:
    @staticmethod
    def group_prescriptions_by_doctor(medicines, tests, notes):
        """Group prescription data by doctor"""
        from collections import defaultdict
        
        prescriptions_per_doctor = defaultdict(lambda: {
            "doctor": None,
            "medicines": [],
            "tests": [],
            "notes": []
        })

        for medicine in medicines:
            doctor_id = medicine.get('doctor_id')
            prescriptions_per_doctor[doctor_id]['medicines'].append(medicine)
            prescriptions_per_doctor[doctor_id]['doctor'] = medicine.get('doctor')

        for test in tests:
            doctor_id = test.get('doctor_id')
            prescriptions_per_doctor[doctor_id]['tests'].append(test)
            prescriptions_per_doctor[doctor_id]['doctor'] = test.get('doctor')

        for note in notes:
            doctor_id = note.get('doctor_id')
            prescriptions_per_doctor[doctor_id]['notes'].append(note)
            prescriptions_per_doctor[doctor_id]['doctor'] = note.get('doctor')

        return list(prescriptions_per_doctor.values())

    @staticmethod
    def format_prescription_summary(prescriptions):
        """Create a summary of prescriptions for display"""
        summary = {
            "total_doctors": len(prescriptions),
            "total_medicines": sum(len(p.get('medicines', [])) for p in prescriptions),
            "total_tests": sum(len(p.get('tests', [])) for p in prescriptions),
            "total_notes": sum(len(p.get('notes', [])) for p in prescriptions),
        }
        return summary