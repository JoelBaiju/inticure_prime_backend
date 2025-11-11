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
        Includes fallback search for next available date (up to 150 days).
        """
        logger.info("==== DoctorFilterService.filter_doctors CALLED ====")
        logger.debug(f"Raw request data: {data}")

        appointment_id = data.get('appointment_id')
        specialization_id = data.get('specialization_id')
        language_info = data.get('language_info', {})
        gender_info = data.get('gender_info', {})
        date_str = data.get('date')
        is_couple = data.get('is_couple', False)

        logger.debug(f"Extracted params -> appointment_id={appointment_id}, specialization_id={specialization_id}, "
                     f"language_info={language_info}, gender_info={gender_info}, date={date_str}, is_couple={is_couple}")

        # Get doctor from user
        try:
            doctor = get_doctor_from_user(user)
            logger.debug(f"Logged-in doctor: {doctor.first_name} ({doctor.doctor_profile_id})")
        except Exception as e:
            logger.error("Failed to resolve doctor from user", exc_info=True)
            return {"error": "Unable to resolve doctor from user"}

        # Convert local date to UTC date
        try:
            datetime_str = f"{date_str}T00:00:00"
            utc_datetime = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
            date = utc_datetime.date()
            logger.debug(f"Converted local date '{date_str}' to UTC date '{date}'")
        except Exception as e:
            logger.error(f"Date conversion failed: {e}", exc_info=True)
            return {"error": f"Invalid date format: {str(e)}"}

        # Validate specialization and appointment
        specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
        appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()

        if not specialization:
            logger.warning(f"Invalid specialization ID: {specialization_id}")
            return {"error": "Invalid specialization ID"}
        if not appointment:
            logger.warning(f"Invalid appointment ID: {appointment_id}")
            return {"error": "Invalid appointment ID"}

        logger.debug(f"Specialization found: {specialization.specialization}")
        logger.debug(f"Appointment found for customer: {appointment.customer.id}")

        session_duration_field = (
            specialization.double_session_duration if is_couple else specialization.single_session_duration
        )
        if session_duration_field is None:
            logger.warning("Session duration not defined.")
            return {"error": "Session duration not defined."}

        # Get preferred doctors
        try:
            logger.info("Fetching preferred doctors...")
            preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
                specialization=specialization.specialization_id,
                language_info=language_info,
                gender_info=gender_info,
                country=appointment.customer.country_details.country_name,
                flag='senior',
                is_couple=is_couple
            )
            logger.debug(f"Preferred doctors fetched -> count={preferred_doctors.count() if preferred_doctors else 0} | "
                         f"gender_matched={gender_matched} | language_matched={language_matched} | fallback={fallback_reason}")
        except Exception as e:
            logger.error("Error while fetching preferred doctors", exc_info=True)
            return {"error": "Error while fetching preferred doctors"}

        # Fallback if no preferred doctors found
        if not preferred_doctors:
            fallback_reason = fallback_reason or "No doctors matched preferences. Showing all available doctors."
            preferred_doctors = DoctorProfiles.objects.filter(
                doctor_flag='senior',
                is_accepted=True,
                payment_assignments__country__country_name=appointment.customer.country_details.country_name,
            ).distinct()
            logger.warning("No preferred doctors found; using all senior doctors for this country.")

        # Step 1: filter doctors for requested date
        logger.info(f"Filtering preferred doctors available on date: {date}")
        preferred_doctors_available_in_date = preferred_doctors.filter(
            doctor_available_hours__start_time__date=date
        ).distinct()

        logger.debug(f"Doctors available on {date} -> {preferred_doctors_available_in_date.count()} found")

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
            for d in preferred_doctors_available_in_date if d != doctor
        ]

        # Step 2: fallback search for next available date (up to 150 days)
        next_available_date = None
        if not result:
            logger.warning(f"No doctors available on {date}. Searching up to 150 days ahead...")
            for i in range(1, 151):
                next_date = date + timedelta(days=i)
                available_next = preferred_doctors.filter(
                    doctor_available_hours__start_time__date=next_date
                ).distinct()
                if available_next.exists():
                    next_available_date = next_date
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
                        for d in available_next if d != doctor
                    ]
                    logger.info(f"Next available date found: {next_available_date} with {len(result)} doctors.")
                    break

            if not next_available_date:
                logger.warning("No available doctors found within 150 days.")

        # Prepare response
        response_data = {
            "available_doctors": result,
            "gender_matched": gender_matched,
            "language_matched": language_matched,
            "fallback_reason": fallback_reason,
        }

        if next_available_date:
            response_data["next_available_date"] = str(next_available_date)

        # Verify JSON serializability
        try:
            json.dumps(response_data, cls=DjangoJSONEncoder)
            logger.debug("Response data JSON serialization successful.")
        except TypeError as e:
            logger.error(f"Response serialization error: {e}", exc_info=True)
            return {"error": f"Data serialization error: {str(e)}"}

        logger.info("==== DoctorFilterService.filter_doctors COMPLETED SUCCESSFULLY ====")
        return response_data
