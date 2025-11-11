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
import logging
import json
import traceback
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from doctor.models import DoctorSpecializations, DoctorProfiles
from general.utils import get_doctor_from_user, convert_local_dt_to_utc

logger = logging.getLogger(__name__)

class DoctorFilterService:
    @staticmethod
    def filter_doctors(user, data):
        """
        Main business logic for filtering doctors based on preferences, with detailed logs.
        """

        logger.info("==== DoctorFilterService.filter_doctors CALLED ====")
        logger.debug(f"Raw input data: {data}")
        logger.debug(f"User: {user}")

        appointment_id = data.get('appointment_id')
        specialization_id = data.get('specialization_id')
        language_info = data.get('language_info', {})
        gender_info = data.get('gender_info', {})
        date_str = data.get('date')
        is_couple = data.get('is_couple', False)

        logger.info(f"appointment_id={appointment_id}, specialization_id={specialization_id}, "
                    f"date={date_str}, is_couple={is_couple}")

        try:
            doctor = get_doctor_from_user(user)
            logger.debug(f"Doctor resolved from user: {doctor} (id={getattr(doctor, 'id', None)})")
        except Exception:
            logger.error("Failed to resolve doctor from user", exc_info=True)
            return {"error": "Unable to resolve doctor from user"}

        if not date_str:
            logger.warning("Date not provided in data")
            return {"error": "Date is required."}

        # Parse date into UTC range
        try:
            datetime_str = f"{date_str}T00:00:00"
            utc_day_start = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
            utc_day_end = utc_day_start + timedelta(days=1)
            logger.debug(f"Converted date to UTC range: {utc_day_start} - {utc_day_end}")
        except Exception as e:
            logger.error(f"Date/time conversion error: {e}", exc_info=True)
            return {"error": f"Date/time conversion error: {str(e)}"}

        # Validate specialization & appointment
        specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
        appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()

        if not specialization:
            logger.warning(f"Invalid specialization ID: {specialization_id}")
            return {"error": "Invalid specialization ID"}
        if not appointment:
            logger.warning(f"Invalid appointment ID: {appointment_id}")
            return {"error": "Invalid appointment ID"}

        logger.debug(f"Specialization: {specialization.specialization}, Appointment: {appointment_id}")

        session_duration_field = (
            specialization.double_session_duration if is_couple else specialization.single_session_duration
        )
        if session_duration_field is None:
            logger.warning("Session duration not defined for specialization.")
            return {"error": "Session duration not defined."}

        # Fetch preferred doctors
        try:
            preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
                gender_info=gender_info,
                language_info=language_info,
                flag='senior',
                country=appointment.customer.country_details.country_name,
                specialization=specialization,
                is_couple=is_couple
            )
            logger.info(f"get_preferred_doctors returned {preferred_doctors.count() if preferred_doctors else 0} doctors")
        except Exception:
            logger.error("Error calling get_preferred_doctors()", exc_info=True)
            return {"error": "Error fetching preferred doctors"}

        if preferred_doctors is None:
            preferred_doctors = DoctorProfiles.objects.none()

        if not preferred_doctors.exists():
            fallback_reason = fallback_reason or "No doctors available with preferences. Showing all available senior doctors."
            logger.info(f"Falling back to all senior doctors for country={appointment.customer.country_details.country_name}")
            preferred_doctors = DoctorProfiles.objects.filter(
                doctor_flag='senior',
                is_accepted=True,
                payment_assignments__country__country_name=appointment.customer.country_details.country_name,
            ).distinct()

        # Filter by specialization
        doctor_specs_qs = DoctorSpecializations.objects.filter(specialization=specialization)
        preferred_doctors = preferred_doctors.filter(doctor_specializations__in=doctor_specs_qs).distinct()
        logger.debug(f"Doctors after specialization filter: {preferred_doctors.count()}")

        # Filter by availability
        preferred_doctors_available_in_date = preferred_doctors.filter(
            doctor_available_hours__start_time__lt=utc_day_end,
            doctor_available_hours__end_time__gt=utc_day_start
        ).distinct()
        logger.info(f"Doctors available in date: {preferred_doctors_available_in_date.count()}")

        # Build result
        result = []
        for d in preferred_doctors_available_in_date:
            if d == doctor:
                continue
            try:
                result.append({
                    "id": d.doctor_profile_id,
                    "name": f"{d.first_name} {d.last_name}",
                    "gender": d.gender,
                    "flag": d.doctor_flag,
                    "specializations": [spec.specialization.specialization for spec in d.doctor_specializations.all()],
                    "languages": [lang.language.language for lang in d.known_languages.all()],
                    "profile_pic": d.profile_pic.url if d.profile_pic else None,
                    "bio": d.doctor_bio,
                })
            except Exception:
                logger.error(f"Error building doctor data for id={d.id}", exc_info=True)

        logger.debug(f"Total doctors in final result: {len(result)}")

        if not result:
            if preferred_doctors.exists():
                fallback_reason = fallback_reason or "Preferred doctors found but none available on requested date."
            else:
                fallback_reason = fallback_reason or "No doctors found for this specialization."
            logger.warning(f"No doctors available after all filters. Reason: {fallback_reason}")

        response_data = {
            "available_doctors": result,
            "gender_matched": gender_matched,
            "language_matched": language_matched,
            "fallback_reason": fallback_reason,
        }

        try:
            json.dumps(response_data, cls=DjangoJSONEncoder)
            logger.info("Response data successfully serialized to JSON.")
        except TypeError as e:
            logger.error(f"Data serialization error: {e}", exc_info=True)
            return {"error": f"Data serialization error: {str(e)}"}

        logger.info("==== DoctorFilterService.filter_doctors COMPLETED ====")
        return response_data
