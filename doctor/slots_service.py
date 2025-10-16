














from datetime import timedelta, datetime, timezone
from collections import defaultdict
from typing import List, Tuple, Dict, Any, Optional, Union
from zoneinfo import ZoneInfo
import logging

from django.utils import timezone as django_timezone
from django.db.models import Q, Prefetch
from django.core.exceptions import ObjectDoesNotExist

from .models import DoctorAvailableHours, DoctorAppointment, DoctorSpecializations, Specializations, DoctorProfiles , DoctorPaymentRules
from general.utils import convert_utc_to_local, round_down_to_nearest_five, round_up_to_nearest_five, get_utc_day_bounds

logger = logging.getLogger(__name__)

# Configuration constants
MIN_DOCTOR_FEE = 2
BREAK_DURATION_MINUTES = 5
JUNIOR_SESSION_DURATION = 15
MAX_FUTURE_DAYS = 180
DEFAULT_BUFFER_HOURS = 0


class SchedulingError(Exception):
    """Custom exception for scheduling-related errors"""
    pass


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Safely convert value to integer with fallback"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def get_timezone_info(tz_value: Union[str, int, float]) -> timezone:
    """
    Return a tzinfo object from an IANA string or numeric offset.
    
    Args:
        tz_value: IANA timezone string (e.g., 'America/New_York') or numeric offset
                 Numeric format: +530 for +05:30, -500 for -05:00
    """
    if isinstance(tz_value, str):
        try:
            return ZoneInfo(tz_value)
        except Exception as e:
            logger.error(f"Invalid timezone string: {tz_value}")
            raise SchedulingError(f"Invalid timezone: {tz_value}")
    
    elif isinstance(tz_value, (int, float)):
        # Handle numeric timezone offsets (e.g., +530 = +05:30)
        try:
            # Determine sign
            sign = 1 if tz_value >= 0 else -1
            abs_value = abs(int(tz_value))
            
            hours = abs_value // 100
            minutes = abs_value % 100
            
            if minutes >= 60:
                raise ValueError("Invalid minutes in timezone offset")
            
            total_minutes = sign * (hours * 60 + minutes)
            return timezone(timedelta(minutes=total_minutes))
        except Exception as e:
            logger.error(f"Invalid numeric timezone: {tz_value}")
            raise SchedulingError(f"Invalid timezone offset: {tz_value}")
    
    else:
        raise SchedulingError("Timezone must be string or numeric")


def subtract_appointments_from_availability(
    availability_start: datetime, 
    availability_end: datetime, 
    appointments: List[Tuple[datetime, datetime]]
) -> List[Tuple[datetime, datetime]]:
    """
    Calculate free time blocks by subtracting appointments from availability.
    
    Args:
        availability_start: Start of available period
        availability_end: End of available period
        appointments: List of (start, end) appointment tuples
    
    Returns:
        List of (start, end) free time blocks
    """
    if not appointments:
        return [(availability_start, availability_end)]
    
    # Sort appointments by start time
    sorted_appointments = sorted(appointments, key=lambda x: x[0])
    free_blocks = []
    current_start = availability_start

    for appt_start, appt_end in sorted_appointments:
        # Add free block before this appointment
        if current_start < appt_start:
            free_blocks.append((current_start, appt_start))
        
        # Move cursor to end of current appointment
        current_start = max(current_start, appt_end)

    # Add remaining free time after last appointment
    if current_start < availability_end:
        free_blocks.append((current_start, availability_end))

    return free_blocks


def generate_clean_slots(
    free_blocks: List[Tuple[datetime, datetime]], 
    session_duration: int, 
    alignment_minutes: int
) -> List[Tuple[datetime, datetime]]:
    """
    Generate aligned time slots from free blocks.
    
    Args:
        free_blocks: List of (start, end) free time periods
        session_duration: Session duration in minutes
        alignment_minutes: Slot alignment in minutes
    
    Returns:
        List of (start, end) available slots
    """
    if alignment_minutes <= 0:
        raise SchedulingError("Alignment minutes must be positive")
    
    clean_slots = []
    duration_td = timedelta(minutes=session_duration)
    break_td = timedelta(minutes=BREAK_DURATION_MINUTES)
    total_required = duration_td + break_td

    for block_start, block_end in free_blocks:
        aligned_start = align_datetime_to_minutes(block_start, alignment_minutes)
        
        # Ensure aligned start is not before the block start
        if aligned_start < block_start:
            aligned_start = align_datetime_to_minutes(
                block_start + timedelta(minutes=alignment_minutes), 
                alignment_minutes
            )

        # Generate slots within this block
        while aligned_start + total_required <= block_end:
            slot = (aligned_start, aligned_start + duration_td)
            clean_slots.append(slot)
            aligned_start += duration_td + break_td

    return clean_slots


def align_datetime_to_minutes(dt: datetime, alignment_minutes: int) -> datetime:
    """Align datetime to the nearest alignment boundary"""
    if alignment_minutes <= 0:
        return dt
    
    current_minutes = dt.minute + dt.second / 60
    aligned_minutes = ((current_minutes // alignment_minutes) + 1) * alignment_minutes
    
    # Handle minute overflow
    if aligned_minutes >= 60:
        extra_hours = int(aligned_minutes // 60)
        aligned_minutes = aligned_minutes % 60
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(
            hours=extra_hours, minutes=int(aligned_minutes)
        )
    
    return dt.replace(minute=int(aligned_minutes), second=0, microsecond=0)


def get_preferred_doctors(
    gender_info: Optional[Dict], 
    language_info: Optional[Dict], 
    flag: str, 
    country: str, 
    specialization: Specializations, 
    is_couple: bool
) -> Tuple[Any, List[int], bool, bool, Optional[str]]:
    """
    Filter doctors based on preferences with fallback logic.
    
    Returns:
        Tuple of (doctors_queryset, doctor_ids, gender_matched, language_matched, fallback_reason)
    """
    # Extract preference values safely
    gender = gender_info.get('value') if gender_info else None
    gender_priority = safe_int_conversion(gender_info.get('priority') if gender_info else None)
    language = language_info.get('value') if language_info else None
    language_priority = safe_int_conversion(language_info.get('priority') if language_info else None)
    
    # Build query filters
    q_gender = Q(gender=gender) if gender else Q()
    q_language = Q(known_languages__language__language__iexact=language) if language else Q()

    logger.info(f"Filtering doctors: gender={gender}, language={language}, flag={flag}, country={country}")

    # Get base doctor queryset with proper prefetching
    doctors = DoctorProfiles.objects.filter(
        doctor_flag=flag,
        is_accepted=True,
        payment_assignments__country__country_name=country,
        payment_assignments__specialization=specialization,
    ).prefetch_related(
        'payment_assignments',
        'known_languages__language'
    ).distinct()

    # Filter by fee requirements
    filtered_doctor_ids = []
    fee_field = "custom_doctor_fee_couple" if is_couple else "custom_doctor_fee_single"
    
    for doctor in doctors:
        for assignment in doctor.payment_assignments.filter(
            country__country_name=country,
            specialization=specialization
        ):
            try:
                effective_payment = assignment.get_effective_payment()
                if effective_payment.get(fee_field, 0) > MIN_DOCTOR_FEE:
                    filtered_doctor_ids.append(doctor.doctor_profile_id)
                    break
            except Exception as e:
                logger.warning(f"Error getting payment for doctor {doctor.doctor_profile_id}: {e}")

    if not filtered_doctor_ids:
        return DoctorProfiles.objects.none(), [], False, False, "No doctors meet fee requirements"

    # Apply fee filter
    doctors = DoctorProfiles.objects.filter(doctor_profile_id__in=filtered_doctor_ids)
    
    # Apply preference filters with fallback logic
    return _apply_preference_filters(doctors, q_gender, q_language, gender_priority, language_priority)


def _apply_preference_filters(
    doctors, q_gender, q_language, gender_priority, language_priority
) -> Tuple[Any, List[int], bool, bool, Optional[str]]:
    """Apply preference filters with intelligent fallback"""
    
    # Try both preferences first
    if q_gender.children and q_language.children:
        preferred = doctors.filter(q_gender & q_language).distinct()
        if preferred.exists():
            ids = list(preferred.values_list("doctor_profile_id", flat=True))
            return preferred, ids, True, True, None
        
        # Fallback based on priority
        higher_priority_filter = q_gender if gender_priority >= language_priority else q_language
        lower_priority_filter = q_language if gender_priority >= language_priority else q_gender
        is_gender_higher = gender_priority >= language_priority
        
        # Try higher priority preference
        preferred = doctors.filter(higher_priority_filter).distinct()
        if preferred.exists():
            ids = list(preferred.values_list("doctor_profile_id", flat=True))
            gender_matched = is_gender_higher
            language_matched = not is_gender_higher
            reason = f"Fallback to {'gender' if is_gender_higher else 'language'} preference only"
            return preferred, ids, gender_matched, language_matched, reason
        
        # Try lower priority preference
        preferred = doctors.filter(lower_priority_filter).distinct()
        if preferred.exists():
            ids = list(preferred.values_list("doctor_profile_id", flat=True))
            gender_matched = not is_gender_higher
            language_matched = is_gender_higher
            reason = f"Fallback to {'language' if is_gender_higher else 'gender'} preference only"
            return preferred, ids, gender_matched, language_matched, reason
    
    # Single preference cases
    elif q_gender.children:
        preferred = doctors.filter(q_gender).distinct()
        if preferred.exists():
            ids = list(preferred.values_list("doctor_profile_id", flat=True))
            return preferred, ids, True, False, None
    
    elif q_language.children:
        preferred = doctors.filter(q_language).distinct()
        if preferred.exists():
            ids = list(preferred.values_list("doctor_profile_id", flat=True))
            return preferred, ids, False, True, None
    
    # No preferences or no matches
    ids = list(doctors.values_list("doctor_profile_id", flat=True))
    reason = "No preferences provided" if not (q_gender.children or q_language.children) else "No doctors matched preferences"
    return doctors, ids, False, False, reason


def get_available_dates(
    doctors, 
    timezone_str: str, 
    session_duration: int, 
    alignment_minutes: int, 
    min_allowed_start: Optional[datetime] = None
) -> List[str]:
    """
    Generate available dates for doctors within the next MAX_FUTURE_DAYS days.
    
    Args:
        doctors: Doctor queryset
        timezone_str: Target timezone
        session_duration: Session duration in minutes
        alignment_minutes: Slot alignment in minutes
        min_allowed_start: Minimum allowed start time (UTC)
    
    Returns:
        List of available dates in ISO format
    """
    try:
        tz = get_timezone_info(timezone_str)
    except SchedulingError:
        logger.error(f"Invalid timezone: {timezone_str}")
        return []
    
    available_dates = []
    now_local = datetime.now(tz)
    
    # Convert min_allowed_start to local timezone if provided
    if min_allowed_start:
        min_local = min_allowed_start.astimezone(tz)
        # Start from the date that contains min_allowed_start
        start_date = min_local.date()
    else:
        # If no buffer, start from today
        min_local = now_local
        start_date = now_local.date()
    
    date_cursor = start_date

    for day_index in range(MAX_FUTURE_DAYS):
        # Determine the start time for this date
        if date_cursor == now_local.date():
            # Today — start from current time or min_allowed_start, whichever is later
            if min_allowed_start:
                start_local = max(now_local, min_local)
            else:
                start_local = now_local
        else:
            # Future days — start from beginning of day or min_allowed if it falls on this day
            start_local = datetime(
                date_cursor.year, 
                date_cursor.month, 
                date_cursor.day, 
                0, 0, tzinfo=tz
            )
            if min_allowed_start and min_local.date() == date_cursor:
                start_local = max(start_local, min_local)
        
        end_local = datetime(
            date_cursor.year, 
            date_cursor.month, 
            date_cursor.day, 
            23, 59, tzinfo=tz
        )

        # Skip if start is after end (can happen with large buffers)
        if start_local >= end_local:
            date_cursor += timedelta(days=1)
            continue

        # Convert to UTC
        start_utc = start_local.astimezone(ZoneInfo("UTC"))
        end_utc = end_local.astimezone(ZoneInfo("UTC"))

        # Check if any slots are available for this date
        slots = generate_slots_for_doctors(
            doctors,
            start_utc,
            end_utc,
            session_duration,
            alignment_minutes,
            min_allowed_start
        )

        if slots:
            available_dates.append(date_cursor.isoformat())

        date_cursor += timedelta(days=1)

    return available_dates

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"

def generate_slots_for_doctors(
    doctors_queryset, 
    target_dt_start: datetime, 
    target_dt_end: datetime,
    session_duration: int, 
    alignment_minutes: int, 
    min_allowed_start: Optional[datetime] = None
) -> Dict[Tuple[datetime, datetime], List[int]]:
    """
    Generate available slots for doctors within a time range.
    
    Args:
        doctors_queryset: Django queryset of doctors
        target_dt_start: Start of target time range (UTC)
        target_dt_end: End of target time range (UTC)
        session_duration: Session duration in minutes
        alignment_minutes: Slot alignment in minutes
        min_allowed_start: Minimum allowed start time
    
    Returns:
        Dictionary mapping (start_time, end_time) to list of available doctor IDs
    """
    if alignment_minutes <= 0:
        raise SchedulingError("Alignment minutes must be positive")
    
    # Round boundaries to nearest 5 minutes
    target_dt_start = round_up_to_nearest_five(target_dt_start)
    target_dt_end = round_down_to_nearest_five(target_dt_end)


    session_duration_td = timedelta(minutes=session_duration)
    alignment_delta = timedelta(minutes=alignment_minutes)
    
        # Prefetch related data to avoid N+1 queries
    doctors_with_data = doctors_queryset.prefetch_related(
        Prefetch(
            'doctor_available_hours',
            queryset=DoctorAvailableHours.objects.filter(
                start_time__lt=target_dt_end,
                end_time__gt=target_dt_start
            ),
            to_attr='relevant_availability'
        ),
        Prefetch(
            'doctor_available_hours', 
            queryset=DoctorAppointment.objects.filter(
                start_time__lt=target_dt_end,
                end_time__gt=target_dt_start
            ),
            to_attr='relevant_appointments'
        )
    )

    temp_slot_pool = defaultdict(set)

    for doctor in doctors_with_data:
        # Get doctor's availability and appointments
        availabilities = [
            (
                _ensure_timezone_aware(a.start_time),
                _ensure_timezone_aware(a.end_time)
            )
            for a in doctor.relevant_availability
        ]
        
        appointments = [
            (
                _ensure_timezone_aware(b.start_time),
                _ensure_timezone_aware(b.end_time)
            )
            for b in doctor.relevant_appointments
        ]
        if len(availabilities)>0:
            logger.debug(f"{GREEN}Doctor {doctor.doctor_profile_id} availabilities: {availabilities}, appointments: {appointments}{RESET}")
        # Generate slots for each availability period
        for avail_start, avail_end in availabilities:
            # Constrain to target range
            constrained_start = max(avail_start, target_dt_start)
            constrained_end = min(avail_end, target_dt_end)
            
            logger.debug(f"{YELLOW}Doctor {doctor.doctor_profile_id} constrained start: {constrained_start} to  constrained_end {constrained_end}{RESET}")

            if constrained_start >= constrained_end:
                continue
            
            # Subtract appointments from this availability period
            free_blocks = subtract_appointments_from_availability(
                constrained_start, constrained_end, appointments
            )
            
            logger.debug(f"{BLUE}Doctor {doctor.doctor_profile_id} free blocks after subtracting appointments: {free_blocks}{RESET}")
            # Generate aligned slots
            for block_start, block_end in free_blocks:
                current_time = _align_to_boundary(block_start, alignment_minutes)
                logger.debug(f"{RED}Doctor {doctor.doctor_profile_id} aligned block start: {current_time} to block end {block_end}{RESET}")
                # Ensure we don't start before the block or minimum allowed time
                if current_time < block_start:
                    logger.debug(f"{RED}Doctor {doctor.doctor_profile_id} current_time {current_time} < block_start {block_start}, realigning{RESET}")
                    current_time = _align_to_boundary(
                        block_start + alignment_delta, alignment_minutes
                    )
                
                if min_allowed_start and current_time < min_allowed_start:
                    logger.debug(f"{RED}Doctor {doctor.doctor_profile_id} current_time {current_time} < min_allowed_start {min_allowed_start}, realigning{RESET}")
                    current_time = _align_to_boundary(min_allowed_start, alignment_minutes)
                
                # Generate slots in this block
                logger.debug(f"{BLUE}Doctor {doctor.doctor_profile_id} generating slots starting at {current_time} until {block_end}{RESET}")
                while current_time + session_duration_td <= block_end:
                    if min_allowed_start is None or current_time >= min_allowed_start:
                        slot_key = (current_time, current_time + session_duration_td)
                        temp_slot_pool[slot_key].add(doctor.doctor_profile_id)
                    
                    current_time += alignment_delta 

    return {k: list(v) for k, v in temp_slot_pool.items()}


def _ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware"""
    if dt.tzinfo is None:
        return django_timezone.make_aware(dt)
    return dt


# def _align_to_boundary(dt: datetime, alignment_minutes: int) -> datetime:
#     """Align datetime to specified minute boundary"""
#     if alignment_minutes <= 0:
#         return dt
    
#     total_minutes = dt.hour * 60 + dt.minute
#     aligned_total = ((total_minutes // alignment_minutes) + 1) * alignment_minutes
    
#     # Handle day overflow
#     if aligned_total >= 24 * 60:
#         next_day = dt.date() + timedelta(days=1)
#         overflow_minutes = aligned_total - 24 * 60
#         return datetime.combine(next_day, datetime.min.time()).replace(
#             minute=overflow_minutes, tzinfo=dt.tzinfo
#         )
    
#     aligned_hour = aligned_total // 60
#     aligned_minute = aligned_total % 60
    
#     return dt.replace(hour=aligned_hour, minute=aligned_minute, second=0, microsecond=0)


def _align_to_boundary(dt: datetime, alignment_minutes: int) -> datetime:
    """Align datetime to the nearest boundary (not always next one)."""
    if alignment_minutes <= 0:
        return dt

    total_minutes = dt.hour * 60 + dt.minute
    remainder = total_minutes % alignment_minutes
    if remainder == 0:
        # Already aligned — no shift needed
        aligned_total = total_minutes
    else:
        aligned_total = ((total_minutes // alignment_minutes) + 1) * alignment_minutes

    # Handle day overflow
    if aligned_total >= 24 * 60:
        next_day = dt.date() + timedelta(days=1)
        overflow_minutes = aligned_total - 24 * 60
        return datetime.combine(next_day, datetime.min.time()).replace(
            minute=overflow_minutes, tzinfo=dt.tzinfo
        )

    aligned_hour = aligned_total // 60
    aligned_minute = aligned_total % 60
    return dt.replace(hour=aligned_hour, minute=aligned_minute, second=0, microsecond=0)



def sort_slots_by_time(slots: List[Dict], local_tz: str) -> List[Dict]:
    """Sort slots by start time in local timezone"""
    try:
        tz = get_timezone_info(local_tz)
        from dateutil import parser
        
        def get_sort_key(slot):
            try:
                return parser.isoparse(slot["start"]).astimezone(tz)
            except Exception as e:
                logger.error(f"Error parsing slot time: {slot['start']}")
                return datetime.min.replace(tzinfo=tz)
        
        slots.sort(key=get_sort_key)
        return slots
    except Exception as e:
        logger.error(f"Error sorting slots: {e}")
        return slots


def get_available_slots(
    specialization_id: Optional[int] = None,
    date_time_start: Optional[datetime] = None,
    date_time_end: Optional[datetime] = None,
    buffer: timedelta = timedelta(hours=DEFAULT_BUFFER_HOURS),
    is_couple: bool = False,
    alignment_minutes: Optional[int] = None,
    is_junior: bool = False,
    gender_info: Optional[Dict] = None,
    language_info: Optional[Dict] = None,
    specialization: str = 'No Specialization',
    country: Optional[str] = None,
    doctor_id: Optional[int] = None,
    timezone_str: str = 'UTC'
) -> Dict[str, Any]:
    """
    Main function to get available appointment slots.
    
    Returns:
        Dictionary containing slots and metadata
    """
    logger.debug(f"\nget_available_slots called with: specialization_id={specialization_id}, date_time_start={date_time_start}, date_time_end={date_time_end}, buffer={buffer}, is_couple={is_couple}, alignment_minutes={alignment_minutes}, is_junior={is_junior}, gender_info={gender_info}, language_info={language_info}, specialization={specialization}, country={country}, doctor_id={doctor_id}, timezone_str={timezone_str}\n")
    try:
        now_utc = django_timezone.now()
        min_allowed_start = now_utc + buffer
        
        alignment_minutes = None
        
        # Handle direct doctor lookup
        if doctor_id:
            return _handle_direct_doctor_lookup(
                doctor_id, date_time_start, date_time_end, 
                alignment_minutes, min_allowed_start, 
                timezone_str, is_couple,specialization_id
            )
        # Validate required parameters
        if not country:
            return {"error": "Country is required"}
        logger.debug(f"Inside get_available_slots line 600 country : {country} , specialization : {specialization} ")

        country_available = DoctorPaymentRules.objects.filter(country__country_name = country , specialization__specialization =specialization).exists()
        if not country_available:
            country = "United States"

        logger.debug(f"Inside get_available_slots line 606 country_available : {country_available} ")
        print(country)
        # Handle specialization-based lookup
        if not specialization_id:
            return {"error": "Specialization ID is required when doctor_id is not provided"}
        
        return _handle_specialization_lookup(
            specialization_id, date_time_start, date_time_end,
            buffer, is_couple, alignment_minutes, is_junior,
            gender_info, language_info, country, timezone_str,
            min_allowed_start
        )
        
    except Exception as e:
        logger.error(f"Error in get_available_slots: {e}")
        return {"error": f"Internal error: {str(e)}"}


def _handle_direct_doctor_lookup(
    doctor_id: int, 
    date_time_start: Optional[datetime], 
    date_time_end: Optional[datetime],
    alignment_minutes: Optional[int], 
    min_allowed_start: datetime,
    timezone_str: str, 
    is_couple: bool,
    specialization_id
) -> Dict[str, Any]:
    """Handle slot generation for a specific doctor"""
    try:
        # Get doctor as a queryset instead of a single object
        doctors = DoctorProfiles.objects.filter(doctor_profile_id=doctor_id)
        
        if not doctors.exists():
            return {"error": "Doctor not found"}
        
        doctor = doctors.first()
        
        # Determine session parameters
        is_junior = doctor.doctor_flag == 'junior'
        
        if is_junior:
            session_duration = JUNIOR_SESSION_DURATION
        else:
            specialization = doctor.doctor_specializations.filter(specialization__specialization_id =specialization_id).first()
            if not specialization:
                return {"error": "Doctor has no specialization"}
            
            specialization_obj = specialization.specialization
            duration_field = (
                specialization_obj.double_session_duration if is_couple 
                else specialization_obj.single_session_duration
            )
            
            if duration_field is None:
                return {"error": "No session duration configured for this specialization"}
            
            session_duration = int(duration_field.total_seconds() // 60)
        
        if alignment_minutes is None:
            if session_duration:
                alignment_minutes = session_duration
            else:                   
                logger.error(f"Session Duration is empty of or not added please confirm")
                return {"Session Duration came empty or not added for this doctors specialization please verify "}
        
        return _generate_slot_response(
            doctors, date_time_start, date_time_end, session_duration,
            alignment_minutes, min_allowed_start, timezone_str,
            True, True, True, None
        )
        
    except Exception as e:
        logger.error(f"Error in direct doctor lookup: {e}")
        return {"error": f"Error processing doctor lookup: {str(e)}"}


def _handle_specialization_lookup(
    specialization_id: int,
    date_time_start: Optional[datetime],
    date_time_end: Optional[datetime],
    buffer: timedelta,
    is_couple: bool,
    alignment_minutes: Optional[int],
    is_junior: bool,
    gender_info: Optional[Dict],
    language_info: Optional[Dict],
    country: str,
    timezone_str: str,
    min_allowed_start: datetime
) -> Dict[str, Any]:
    """Handle slot generation based on specialization and preferences"""
    try:
        specialization_obj = Specializations.objects.get(specialization_id=specialization_id)
    except Specializations.DoesNotExist:
        return {"error": "Specialization not found"}
    
    logger.debug(f"handle specialization lookup Specialization found: {specialization_obj.specialization} , country : {country} , is_junior : {is_junior}   ,is_couple : {is_couple}     ")
    # Get session duration
    if is_junior:
        session_duration = JUNIOR_SESSION_DURATION
        flag = "junior"
    else:
        duration_field = (
            specialization_obj.double_session_duration if is_couple 
            else specialization_obj.single_session_duration
        )
        if duration_field is None:
            return {"error": "No session duration configured for this specialization"}
        
        session_duration = int(duration_field.total_seconds() // 60)
        flag = "senior"
    
    if alignment_minutes is None:
        alignment_minutes = session_duration
    
    # Get preferred doctors
    doctors, _, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
        gender_info, language_info, flag, country, specialization_obj, is_couple
    )
    
    # For senior doctors, ensure they have the required specialization
    if not is_junior:
        doctor_specs = DoctorSpecializations.objects.filter(specialization=specialization_obj)
        original_doctors = doctors
        doctors = doctors.filter(doctor_specializations__in=doctor_specs).distinct()
        
        if not doctors.exists() and original_doctors.exists():
            # Fallback to all doctors with specialization
            all_senior_doctors = DoctorProfiles.objects.filter(
                doctor_flag="senior",
                doctor_specializations__in=doctor_specs,
                is_accepted=True,
                payment_assignments__country__country_name=country,
            ).distinct()
            doctors = all_senior_doctors
            fallback_reason = "No preferred doctors with specialization, showing all qualified doctors"
            gender_matched = False
            language_matched = False
    
    if not doctors.exists():
        return {
            "slots": [],
            "matched_preferences": False,
            "gender_matched": False,
            "language_matched": False,
            "fallback_reason": "No doctors available",
            "doctors_found_but_unavailable": False,
            "available_dates": [],
            "current_date": None
        }
    
    return _generate_slot_response(
        doctors, date_time_start, date_time_end, session_duration,
        alignment_minutes, min_allowed_start, timezone_str,
        gender_matched, language_matched, 
        gender_matched or language_matched, fallback_reason
    )


def _generate_slot_response(
    doctors,
    date_time_start: Optional[datetime],
    date_time_end: Optional[datetime],
    session_duration: int,
    alignment_minutes: int,
    min_allowed_start: datetime,
    timezone_str: str,
    gender_matched: bool,
    language_matched: bool,
    matched_preferences: bool,
    fallback_reason: Optional[str]
) -> Dict[str, Any]:
    """Generate the final slot response with fallback logic"""
    
    formatted_slots = []
    
    # Generate slots for the specified time range
    if date_time_start and date_time_end:
        slot_pool = generate_slots_for_doctors(
            doctors, date_time_start, date_time_end, 
            session_duration, alignment_minutes, min_allowed_start
        )
        formatted_slots = _format_slots(slot_pool, timezone_str)
    
    # Get available dates (this will respect the buffer/min_allowed_start)
    available_dates = get_available_dates(
        doctors, timezone_str, session_duration, alignment_minutes, min_allowed_start
    )
    
    doctors_found_but_unavailable = False
    
    # If no slots found in the specified range but doctors exist, try next available date
    if not formatted_slots and doctors.exists() and available_dates:
        doctors_found_but_unavailable = True
        
        # Get slots for the next available date
        next_date = available_dates[0]
        try:
            next_date_start, next_date_end = get_utc_day_bounds(next_date, timezone_str)
            slot_pool = generate_slots_for_doctors(
                doctors, next_date_start, next_date_end,
                session_duration, alignment_minutes, min_allowed_start
            )
            formatted_slots = _format_slots(slot_pool, timezone_str)
            
            if formatted_slots:
                fallback_reason = (
                    fallback_reason or 
                    "No slots available for selected date, showing next available date"
                )
                doctors_found_but_unavailable = False
                
        except Exception as e:
            logger.error(f"Error getting slots for next available date: {e}")

    return {
        "slots": sort_slots_by_time(formatted_slots, timezone_str),
        "matched_preferences": matched_preferences,
        "gender_matched": gender_matched,
        "language_matched": language_matched,
        "fallback_reason": fallback_reason,
        "doctors_found_but_unavailable": doctors_found_but_unavailable,
        "available_dates": available_dates,
        "current_date": formatted_slots[0]["start"][0:10] if formatted_slots else None
    }



def _format_slots(slot_pool: Dict, timezone_str: str) -> List[Dict[str, Any]]:
    """Format slot pool into user-friendly format"""
    formatted_slots = []
    
    for (start_utc, end_utc), doctor_ids in slot_pool.items():
        try:
            start_local = convert_utc_to_local(start_utc.isoformat(), timezone_str)
            end_local = convert_utc_to_local(end_utc.isoformat(), timezone_str)
            
            formatted_slots.append({
                "start": start_local,
                "end": end_local,
                "available_doctors": doctor_ids,
                "doctors_count":len(doctor_ids),
            })
        except Exception as e:
            logger.error(f"Error formatting slot {start_utc} - {end_utc}: {e}")
            continue
    
    return formatted_slots