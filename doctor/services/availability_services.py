from datetime import datetime, time, date as dt_date
import pytz
from doctor.models import DoctorAvailableHours , DoctorAppointment
from general.utils import (
    convert_utc_to_local_return_dt,
    convert_doctor_request_datetime_to_utc
)


class InvalidTimeFormat(Exception): pass
class EndBeforeStart(Exception): pass


def get_available_hours(doctor_profile, date_str=None):
    """Return all availability blocks for a given date (default today)."""
    local_tz = pytz.timezone(doctor_profile.time_zone)
    if date_str:
        local_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        local_date = dt_date.today()

    start_of_day_local = datetime.combine(local_date, time.min)
    end_of_day_local = datetime.combine(local_date, time.max)

    start_of_day_utc = local_tz.localize(start_of_day_local).astimezone(pytz.UTC)
    end_of_day_utc = local_tz.localize(end_of_day_local).astimezone(pytz.UTC)

    hours_qs = DoctorAvailableHours.objects.filter(
        doctor=doctor_profile,
        start_time__gte=start_of_day_utc,
        start_time__lte=end_of_day_utc,
    ).order_by("start_time")

    return [
        {
            "date": convert_utc_to_local_return_dt(entry.start_time, doctor_profile.time_zone).date(),
            "start_date_time": convert_utc_to_local_return_dt(entry.start_time, doctor_profile.time_zone),
            "start_time": convert_utc_to_local_return_dt(entry.start_time, doctor_profile.time_zone).time(),
            "end_time": convert_utc_to_local_return_dt(entry.end_time, doctor_profile.time_zone).time(),
        }
        for entry in hours_qs
    ]


def save_availability_blocks(doctor_profile, dates, start_time_str, end_time_str):
    """Save availability blocks, merging overlaps if needed."""
    try:
        start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()
    except (TypeError, ValueError):
        raise InvalidTimeFormat()

    if end_time_obj <= start_time_obj:
        raise EndBeforeStart()

    for date_str in dates:
        start_datetime_utc = convert_doctor_request_datetime_to_utc(
            date_str, start_time_str, doctor_profile
        )
        end_datetime_utc = convert_doctor_request_datetime_to_utc(
            date_str, end_time_str, doctor_profile
        )

        overlapping_qs = DoctorAvailableHours.objects.filter(
            doctor=doctor_profile,
            start_time__lt=end_datetime_utc,
            end_time__gt=start_datetime_utc
        )

        if overlapping_qs.exists():
            earliest_start = min([start_datetime_utc] + [b.start_time for b in overlapping_qs])
            latest_end = max([end_datetime_utc] + [b.end_time for b in overlapping_qs])
            main_block = overlapping_qs.first()
            main_block.start_time = earliest_start
            main_block.end_time = latest_end
            main_block.save()
            overlapping_qs.exclude(id=main_block.id).delete()
        else:
            DoctorAvailableHours.objects.create(
                doctor=doctor_profile,
                start_time=start_datetime_utc,
                end_time=end_datetime_utc
            )

    return {
        "message": "Availability block(s) saved successfully.",
        "dates": dates,
        "start_time": convert_utc_to_local_return_dt(start_datetime_utc, doctor_profile.time_zone).time(),
        "end_time": convert_utc_to_local_return_dt(end_datetime_utc, doctor_profile.time_zone).time(),
    }









from ..models import DoctorProfiles
from general.utils import (
    get_doctor_timezone_from_user,
    get_current_time_in_utc_from_tz,
    convert_local_dt_to_utc,
)
from ..slots_service import get_available_slots


def fetch_available_slots(user, doctor_id ,specialization_id, preferred_date=None,country=None , timezone_str=None):
    # Validate doctor
    doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)

    # Timezone
    if user.is_superuser:
        timezone_str = "Asia/Calcutta"
    else:
        # timezone_str = get_doctor_timezone_from_user(user)
        timezone_str = timezone_str

    if not timezone_str:
        raise Exception("Doctor time zone not set")

    # Default base date (doctor's current day in UTC)
    base_date, end_of_base_date = get_current_time_in_utc_from_tz(timezone_str)

    # If preferred date given, convert to UTC window
    if preferred_date:
        preferred_dt_start = convert_local_dt_to_utc(f"{preferred_date}T00:00:00", timezone_str)
        preferred_dt_end = convert_local_dt_to_utc(f"{preferred_date}T23:59:59", timezone_str)
    else:
        preferred_dt_start, preferred_dt_end = base_date, end_of_base_date

    # Fetch available slots
    results = get_available_slots(
        doctor_id=doctor_id,
        date_time_start=preferred_dt_start,
        date_time_end=preferred_dt_end,
        timezone_str=timezone_str,
        country=country,
        specialization_id=specialization_id
    )
    # results["current_date"] = str(preferred_dt_start.date())

    # If no slots → fallback to next available date
    results = fallback_to_next_available_date(
        doctor_id, timezone_str, results, preferred_dt_start, results.get("available_dates", [])
    )

    return results


def fallback_to_next_available_date(doctor_id, timezone_str, results, preferred_dt_start, available_dates):
    slots = results.get("slots", [])
    if not slots and available_dates:
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
                timezone_str=timezone_str,
            )

            if next_results.get("slots"):
                # next_results["current_date"] = str(next_dt_start.date())
                return next_results

    # If still nothing, return same results with current_date
    # results["current_date"] = str(preferred_dt_start.date())
    return results











def edit_availability_block(data):

    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    old_start_time_str = data.get("old_start_time")
    doctor_id = data.get("doctor_id")
    date = data.get("date")
    doctor_profile = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)

    start_time_utc = convert_doctor_request_datetime_to_utc(date, start_time_str, doctor_profile)
    end_time_utc = convert_doctor_request_datetime_to_utc(date , end_time_str, doctor_profile)
    old_start_time_utc = convert_local_dt_to_utc(old_start_time_str, doctor_profile.time_zone)

    existing_appointments = DoctorAppointment.objects.filter(
        doctor=doctor_profile,
        appointment__appointment_status__in=["confirmed"],
        start_time__gte=old_start_time_utc
    )

    if existing_appointments:
        appointment_ids = str([appt.appointment.appointment_id for appt in existing_appointments])  
        raise Exception(f"Cannot edit block with confirmed appointments {appointment_ids} , tried to edit block starting at {old_start_time_str} in timezone {doctor_profile.time_zone} , {old_start_time_utc} in utc to new time {start_time_str} - {end_time_str} in timezone {doctor_profile.time_zone} , {start_time_utc} - {end_time_utc} in utc")
    
    try:
        block = DoctorAvailableHours.objects.get(
            doctor=doctor_profile,
            start_time=old_start_time_utc
        )
    except DoctorAvailableHours.DoesNotExist:
        raise Exception("Availability block not found")
    
    if block:
        block.start_time = start_time_utc
        block.end_time = end_time_utc
        block.save()

    return {
        "message": "Availability block updated successfully.",}