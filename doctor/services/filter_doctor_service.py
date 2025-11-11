import json
from django.core.serializers.json import DjangoJSONEncoder
from general.utils import convert_local_dt_to_utc
from doctor.models import DoctorProfiles, Specializations
from analysis.models import AppointmentHeader
from ..slots_service import get_preferred_doctors  # assuming you already have this


# class DoctorFilterService:
#     @staticmethod
#     def filter_doctors(user, data):
#         """
#         Main business logic for filtering doctors based on preferences.
#         """

#         appointment_id = data.get('appointment_id')
#         specialization_id = data.get('specialization_id')
#         language_info = data.get('language_info', {})
#         gender_info = data.get('gender_info', {})
#         date_str = data.get('date')
#         is_couple = data.get('is_couple', False)

#         # Get doctor from user
#         from doctor.utils import get_doctor_from_user
#         doctor = get_doctor_from_user(user)

#         # Parse date into UTC
#         datetime_str = f"{date_str}T00:00:00"
#         utc_datetime = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
#         date = utc_datetime.date()

#         specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
#         appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()

#         if not specialization:
#             return ("Invalid specialization ID")
#         if not appointment:
#             return ("Invalid appointment ID")

#         session_duration_field = (
#             specialization.double_session_duration if is_couple else specialization.single_session_duration
#         )
#         if session_duration_field is None:
#             return ("Session duration not defined.")
#         print(specialization.specialization)

#         preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
#             specialization=specialization.specialization_id,
#             language_info=language_info,
#             gender_info=gender_info,
#             country=appointment.customer.country_details.country_name,
#             flag='senior',
#             is_couple=is_couple
#         )

#         if not preferred_doctors:
#             fallback_reason = fallback_reason or "No doctors available with preferences. Showing all available doctors."
#             preferred_doctors = DoctorProfiles.objects.filter(
#                 doctor_flag='senior',
#                 is_accepted=True,
#                 payment_assignments__country__country_name=appointment.customer.country_details.country_name,
#             ).distinct()
#             result = []
#         else:
#             preferred_doctors_available_in_date = preferred_doctors.filter(
#                 doctor_available_hours__start_time__date=date
#             ).distinct()

#             result = [
                
#                 {
#                     "id": doctor2.doctor_profile_id,
#                     "name": f"{doctor2.first_name} {doctor2.last_name}",
#                     "gender": doctor2.gender,
#                     "flag": doctor2.doctor_flag,
#                     "specializations": [spec.specialization.specialization for spec in doctor2.doctor_specializations.all()],
#                     "languages": [lang.language.language for lang in doctor2.known_languages.all()],
#                     "profile_pic": doctor2.profile_pic.url if doctor2.profile_pic else None,
#                     "bio": doctor2.doctor_bio,
#                 }
#                 for doctor2 in preferred_doctors_available_in_date 
#                 if doctor2 != doctor
#             ]
#         print(f"Filtered doctors: {result}")
#         response_data = {
#             "available_doctors": result,
#             "gender_matched": gender_matched,
#             "language_matched": language_matched,
#             "fallback_reason": fallback_reason,
#         }

#         # Ensure JSON serializability
#         try:
#             json.dumps(response_data, cls=DjangoJSONEncoder)
#         except TypeError as e:
#              return(f"Data serialization error: {str(e)}")

#         return response_data



from datetime import timedelta
from doctor.models import DoctorSpecializations

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

        # Validate inputs
        if not date_str:
            return ("Date is required.")

        # Parse date into UTC day bounds (00:00:00 to 23:59:59) using doctor's timezone
        # Keep the same conversion utility you used (convert_local_dt_to_utc) if it returns an aware datetime
        try:
            datetime_str = f"{date_str}T00:00:00"
            utc_day_start = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
            # start of day utc already returned; build end of day
            utc_day_end = utc_day_start + timedelta(days=1)  # exclusive upper bound
        except Exception as e:
            return (f"Date/time conversion error: {str(e)}")

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
        # print(specialization.specialization)

        # IMPORTANT: pass the specialization object (not the string or id) to get_preferred_doctors
        preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
            gender_info=gender_info,
            language_info=language_info,
            flag='senior',
            country=appointment.customer.country_details.country_name,
            specialization=specialization,   # pass object
            is_couple=is_couple
        )

        # If get_preferred_doctors returns None-like queryset, normalize
        if preferred_doctors is None:
            preferred_doctors = DoctorProfiles.objects.none()

        # If no preferred doctors at all, fallback to all senior doctors with payment assignment in the country
        if not preferred_doctors.exists():
            fallback_reason = fallback_reason or "No doctors available with preferences. Showing all available senior doctors."
            preferred_doctors = DoctorProfiles.objects.filter(
                doctor_flag='senior',
                is_accepted=True,
                payment_assignments__country__country_name=appointment.customer.country_details.country_name,
            ).distinct()

        # For senior doctors ensure they actually have the requested specialization (same logic as reference)
        doctor_specs_qs = DoctorSpecializations.objects.filter(specialization=specialization)
        preferred_doctors = preferred_doctors.filter(doctor_specializations__in=doctor_specs_qs).distinct()

        # Now find doctors whose availability overlaps the UTC day bounds.
        # Use range overlap semantics: start_time < utc_day_end AND end_time > utc_day_start
        preferred_doctors_available_in_date = preferred_doctors.filter(
            doctor_available_hours__start_time__lt=utc_day_end,
            doctor_available_hours__end_time__gt=utc_day_start
        ).distinct()

        # Build result excluding the requesting doctor
        result = [
            {
                "id": d.doctor_profile_id,
                "name": f"{d.first_name} {d.last_name}",
                "gender": d.gender,
                "flag": d.doctor_flag,
                "specializations": [spec.specialization.specialization for spec in d.doctor_specializations.all()],
                "languages": [lang.language.language for lang in d.known_languages.all()],
                "profile_pic": d.profile_pic.url if d.profile_pic else None,
                "bio": d.doctor_bio,
            }
            for d in preferred_doctors_available_in_date
            if d != doctor
        ]

        if not result:
            # if there are preferred doctors but none available on the chosen date, clarify fallback
            if preferred_doctors.exists():
                fallback_reason = fallback_reason or "Preferred doctors found but none available on requested date."
            else:
                fallback_reason = fallback_reason or "No doctors found for this specialization."

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
            return (f"Data serialization error: {str(e)}")

        return response_data
