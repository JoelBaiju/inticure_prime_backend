import json
from django.core.serializers.json import DjangoJSONEncoder
from general.utils import convert_local_dt_to_utc
from doctor.models import DoctorProfiles, Specializations
from analysis.models import AppointmentHeader
from ..slots_service import get_preferred_doctors  # assuming you already have this


class DoctorFilterService:
    @staticmethod
    def filter_doctors(user, data):
        """
        Main business logic for filtering doctors based on preferences.
        """

        appointment_id = data.get('appointment_id')
        specialization_id = data.get('specialization_id')
        language_info = data.get('language_info', {})
        gender_info = data.get('gender_info', {})
        date_str = data.get('date')
        is_couple = data.get('is_couple', False)

        # Get doctor from user
        from doctor.utils import get_doctor_from_user
        doctor = get_doctor_from_user(user)

        # Parse date into UTC
        datetime_str = f"{date_str}T00:00:00"
        utc_datetime = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
        date = utc_datetime.date()

        specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
        appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()

        if not specialization:
            return ("Invalid specialization ID")
        if not appointment:
            return ("Invalid appointment ID")

        session_duration_field = (
            specialization.double_session_duration if is_couple else specialization.single_session_duration
        )
        if session_duration_field is None:
            return ("Session duration not defined.")
        print(specialization.specialization)

        preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
            specialization=specialization.specialization_id,
            language_info=language_info,
            gender_info=gender_info,
            country=appointment.customer.country_details.country_name,
            flag='senior',
            is_couple=is_couple
        )

        if not preferred_doctors:
            fallback_reason = fallback_reason or "No doctors available with preferences. Showing all available doctors."
            preferred_doctors = DoctorProfiles.objects.filter(
                doctor_flag='senior',
                is_accepted=True,
                payment_assignments__country__country_name=appointment.customer.country_details.country_name,
            ).distinct()
            result = []
        else:
            preferred_doctors_available_in_date = preferred_doctors.filter(
                doctor_available_hours__start_time__date=date
            ).distinct()

            result = [
                
                {
                    "id": doctor2.doctor_profile_id,
                    "name": f"{doctor2.first_name} {doctor2.last_name}",
                    "gender": doctor2.gender,
                    "flag": doctor2.doctor_flag,
                    "specializations": [spec.specialization.specialization for spec in doctor2.doctor_specializations.all()],
                    "languages": [lang.language.language for lang in doctor2.known_languages.all()],
                    "profile_pic": doctor2.profile_pic.url if doctor2.profile_pic else None,
                }
                for doctor2 in preferred_doctors_available_in_date 
                if doctor2 != doctor
            ]
        print(f"Filtered doctors: {result}")
        response_data = {
            "available_doctors": result,
            "gender_matched": gender_matched,
            "language_matched": language_matched,
            "fallback_reason": fallback_reason,
        }

        # Ensure JSON serializability
        try:
            json.dumps(response_data, cls=DjangoJSONEncoder)
        except TypeError as e:
             return(f"Data serialization error: {str(e)}")

        return response_data
