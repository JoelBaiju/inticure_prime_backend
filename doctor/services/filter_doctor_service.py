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

class DoctorFilterService:
    @staticmethod
    def filter_doctors(user, data):
        """
        Filters doctors by preference and returns available ones.
        If none are available for the given date, automatically searches for the next available date.
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

        logger.info(f"appointment_id={appointment_id}, specialization_id={specialization_id}, date={date_str}, is_couple={is_couple}")

        # Validate date
        if not date_str:
            logger.warning("Date not provided in data")
            return {"error": "Date is required."}

        # Resolve doctor from user
        try:
            doctor = get_doctor_from_user(user)
            logger.debug(f"Doctor resolved from user: {doctor} (id={getattr(doctor, 'doctor_profile_id', None)})")
        except Exception as e:
            logger.error("Failed to resolve doctor from user", exc_info=True)
            return {"error": "Unable to resolve doctor from user"}

        # Convert local date to UTC range
        try:
            datetime_str = f"{date_str}T00:00:00"
            utc_day_start = convert_local_dt_to_utc(datetime_str, doctor.time_zone)
            utc_day_end = utc_day_start + timedelta(days=1)
            logger.debug(f"Converted date to UTC range: {utc_day_start} - {utc_day_end}")
        except Exception as e:
            logger.error(f"Date/time conversion error: {e}", exc_info=True)
            return {"error": f"Date/time conversion error: {str(e)}"}

        # Validate specialization and appointment
        specialization = Specializations.objects.filter(specialization_id=specialization_id).first()
        appointment = AppointmentHeader.objects.filter(appointment_id=appointment_id).first()

        if not specialization:
            logger.warning(f"Invalid specialization ID: {specialization_id}")
            return {"error": "Invalid specialization ID"}
        if not appointment:
            logger.warning(f"Invalid appointment ID: {appointment_id}")
            return {"error": "Invalid appointment ID"}

        logger.debug(f"Specialization: {specialization.specialization}, Appointment: {appointment_id}")

        session_duration = (
            specialization.double_session_duration if is_couple else specialization.single_session_duration
        )
        if session_duration is None:
            logger.warning("Session duration not defined for specialization.")
            return {"error": "Session duration not defined."}

        # Step 1: get preferred doctors
        try:
            # from doctor..scheduler_utils import get_preferred_doctors
            preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
                gender_info=gender_info,
                language_info=language_info,
                flag='senior',
                country=appointment.customer.country_details.country_name,
                specialization=specialization,
                is_couple=is_couple
            )
            logger.info(f"Preferred doctors count: {preferred_doctors.count() if preferred_doctors else 0}")
        except Exception as e:
            logger.error("Error in get_preferred_doctors()", exc_info=True)
            return {"error": "Error fetching preferred doctors"}

        # Apply specialization filtering
        doctor_specs_qs = DoctorSpecializations.objects.filter(specialization=specialization)
        preferred_doctors = preferred_doctors.filter(doctor_specializations__in=doctor_specs_qs).distinct()
        logger.debug(f"Doctors after specialization filter: {preferred_doctors.count()}")

        # Step 2: filter available doctors for the selected date
        preferred_doctors_available_in_date = preferred_doctors.filter(
            doctor_available_hours__start_time__lt=utc_day_end,
            doctor_available_hours__end_time__gt=utc_day_start
        ).distinct()
        logger.info(f"Doctors available for requested date: {preferred_doctors_available_in_date.count()}")

        # If no doctors are available, find next available date
        if not preferred_doctors_available_in_date.exists():
            logger.warning("No doctors available for requested date. Searching for next available date...")

            try:
                available_dates = get_available_dates(
                    doctors=preferred_doctors,
                    timezone_str=doctor.time_zone,
                    session_duration=session_duration,
                    alignment_minutes=5,
                    min_allowed_start=utc_day_end  # search from next day onwards
                )
            except Exception as e:
                logger.error("Error fetching available dates", exc_info=True)
                return {"error": "Error fetching next available dates"}

            if not available_dates:
                logger.warning("No available dates found within limit.")
                return {
                    "available_doctors": [],
                    "next_available_date": None,
                    "message": "No doctors available in upcoming days."
                }

            next_available_date = available_dates[0]
            logger.info(f"Next available date found: {next_available_date}")

            # Get slots for that next available date
            next_date_obj = datetime.fromisoformat(next_available_date)
            utc_start = convert_local_dt_to_utc(f"{next_available_date}T00:00:00", doctor.time_zone)
            utc_end = utc_start + timedelta(days=1)

            slots = generate_slots_for_doctors(
                doctors_queryset=preferred_doctors,
                target_dt_start=utc_start,
                target_dt_end=utc_end,
                session_duration=session_duration,
                alignment_minutes=5
            )

            logger.debug(f"Slots generated for next available date: {len(slots)}")
            return {
                "available_doctors": [],
                "next_available_date": next_available_date,
                "available_slots": {str(k[0]): v for k, v in slots.items()},
                "message": f"No doctors available on {date_str}, showing next available date {next_available_date}."
            }

        # Step 3: return available doctors for requested date
        result = []
        for d in preferred_doctors_available_in_date:
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
