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

#         return response_dataimport logging
import json
from datetime import timedelta, datetime
from django.core.serializers.json import DjangoJSONEncoder
from doctor.models import DoctorSpecializations, DoctorProfiles
from general.utils import get_doctor_from_user, convert_local_dt_to_utc
from ..slots_service import (
    get_preferred_doctors,
    get_available_dates,
    generate_slots_for_doctors
)
import logging
logger = logging.getLogger(__name__)

import traceback

class DoctorFilterService:
    @staticmethod
    def filter_doctors(user, data):
        """
        Main business logic for filtering doctors based on preferences.
        Includes detailed logging for debugging.
        """

        logger.info("DoctorFilterService.filter_doctors called with data: %s", data)

        try:
            appointment_id = data.get('appointment_id')
            specialization_id = data.get('specialization_id')
            language_info = data.get('language_info', {})
            gender_info = data.get('gender_info', {})
            date_str = data.get('date')
            is_couple = data.get('is_couple', False)

            logger.debug(
                "Extracted params -> appointment_id=%s, specialization_id=%s, "
                "language_info=%s, gender_info=%s, date=%s, is_couple=%s",
                appointment_id, specialization_id, language_info, gender_info, date_str, is_couple
            )

            # Get doctor from user
            from doctor.utils import get_doctor_from_user
            doctor = get_doctor_from_user(user)
            logger.debug("Logged-in doctor: %s (%s)", doctor.first_name, doctor.doctor_profile_id)

            # Parse date into UTC
            datetime_str = f"{date_str}T00:00:00"
            utc_datetime = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
            date = utc_datetime.date()
            logger.debug("Converted local date '%s' to UTC date '%s'", date_str, date)

            specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
            appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()

            if not specialization:
                logger.error("Invalid specialization ID: %s", specialization_id)
                return "Invalid specialization ID"
            if not appointment:
                logger.error("Invalid appointment ID: %s", appointment_id)
                return "Invalid appointment ID"

            logger.debug("Specialization found: %s", specialization.specialization)
            logger.debug("Appointment found for customer: %s", appointment.customer_id)

            # Determine session duration
            session_duration_field = (
                specialization.double_session_duration if is_couple else specialization.single_session_duration
            )
            if session_duration_field is None:
                logger.error("Session duration undefined for specialization %s", specialization.specialization)
                return "Session duration not defined."

            # Fetch preferred doctors
            logger.info("Fetching preferred doctors...")
            preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
                specialization=specialization.specialization_id,
                language_info=language_info,
                gender_info=gender_info,
                country=appointment.customer.country_details.country_name,
                flag='senior',
                is_couple=is_couple
            )
            logger.debug(
                "Preferred doctors fetched -> count=%s | gender_matched=%s | language_matched=%s | fallback=%s",
                preferred_doctors.count() if preferred_doctors else 0,
                gender_matched,
                language_matched,
                fallback_reason
            )

            if not preferred_doctors:
                fallback_reason = fallback_reason or "No doctors available with preferences. Showing all available doctors."
                logger.warning("No preferred doctors found. Falling back: %s", fallback_reason)

                preferred_doctors = DoctorProfiles.objects.filter(
                    doctor_flag='senior',
                    is_accepted=True,
                    payment_assignments__country__country_name=appointment.customer.country_details.country_name,
                ).distinct()
                result = []
            else:
                logger.info("Filtering preferred doctors available on date: %s", date)
                preferred_doctors_available_in_date = preferred_doctors.filter(
                    doctor_available_hours__start_time__date=date
                ).distinct()

                logger.debug(
                    "Doctors available on %s -> %s found",
                    date,
                    preferred_doctors_available_in_date.count()
                )

                result = []
                for doctor2 in preferred_doctors_available_in_date:
                    if doctor2 == doctor:
                        logger.debug("Skipping logged-in doctor from result: %s", doctor2.first_name)
                        continue

                    result.append({
                        "id": doctor2.doctor_profile_id,
                        "name": f"{doctor2.first_name} {doctor2.last_name}",
                        "gender": doctor2.gender,
                        "flag": doctor2.doctor_flag,
                        "specializations": [spec.specialization.specialization for spec in doctor2.doctor_specializations.all()],
                        "languages": [lang.language.language for lang in doctor2.known_languages.all()],
                        "profile_pic": doctor2.profile_pic.url if doctor2.profile_pic else None,
                        "bio": doctor2.doctor_bio,
                    })

                logger.info("Total filtered available doctors: %s", len(result))

            response_data = {
                "available_doctors": result,
                "gender_matched": gender_matched,
                "language_matched": language_matched,
                "fallback_reason": fallback_reason,
            }

            try:
                json.dumps(response_data, cls=DjangoJSONEncoder)
                logger.debug("Response data JSON serialization successful.")
            except TypeError as e:
                logger.exception("Data serialization error: %s", str(e))
                return f"Data serialization error: {str(e)}"

            logger.info("DoctorFilterService completed successfully.")
            return response_data

        except Exception as e:
            logger.error("Unhandled exception in filter_doctors: %s", str(e))
            logger.error(traceback.format_exc())
            return f"Unexpected error: {str(e)}"
