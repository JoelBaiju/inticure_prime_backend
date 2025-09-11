from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from django.db.models import Q, Prefetch
from django.utils import timezone as django_timezone
from zoneinfo import ZoneInfo
import logging

# Import your existing models and utilities
from doctor.models import DoctorProfiles, DoctorSpecializations, Specializations, DoctorAvailableHours, DoctorAppointment
from general.utils import get_utc_day_bounds
from doctor.slots_service import subtract_appointments_from_availability
logger = logging.getLogger(__name__)
def get_available_doctors_for_specialization(
    specialization_id: int,
    country: str,
    start_time: datetime = None,
    end_time: datetime = None
) -> Optional[List[Dict[str, Any]]]:

    # try:
        # Validate specialization exists
        try:
            specialization = Specializations.objects.get(specialization_id=specialization_id)
        except Specializations.DoesNotExist:
            logger.error(f"Specialization with ID {specialization_id} not found")
            return None
        
    
        # Build base query for doctors with the specialization
        doctors_query = DoctorProfiles.objects.filter(
            doctor_specializations__specialization=specialization,
            is_accepted=True,
            payment_assignments__country__country_name=country,
            payment_assignments__specialization=specialization,
        )
        
    
        # Prefetch related data to avoid N+1 queries
        doctors_with_data = doctors_query.prefetch_related(
            Prefetch(
                'doctor_available_hours',
                queryset=DoctorAvailableHours.objects.filter(
                    start_time__lt=end_time,
                    end_time__gt=start_time
                ),
                to_attr='relevant_availability'
            ),
            Prefetch(
                'doctor_appointment',
                queryset=DoctorAppointment.objects.filter(
                    start_time__lt=end_time,
                    end_time__gt=start_time
                ),
                to_attr='relevant_appointments'
            ),
            'payment_assignments',
            'known_languages__language',
            'doctor_specializations__specialization'
        ).distinct()
        
        available_doctors = []
        # fee_field = "custom_doctor_fee_couple" if is_couple else "custom_doctor_fee_single"
        
        for doctor in doctors_with_data:
            # # Check if doctor meets minimum fee requirements
            # has_valid_payment = False
            # doctor_fee = 0
            
            # for assignment in doctor.payment_assignments.filter(
            #     country__country_name=country,
            #     specialization=specialization
            # ):
            #     try:
            #         effective_payment = assignment.get_effective_payment()
            #         doctor_fee = effective_payment.get(fee_field, 0)
            #         if doctor_fee > MIN_DOCTOR_FEE:  # Using your existing constant
            #             has_valid_payment = True
            #             break
            #     except Exception as e:
            #         logger.warning(f"Error getting payment for doctor {doctor.doctor_profile_id}: {e}")
            
            # if not has_valid_payment:
            #     logger.debug(f"Doctor {doctor.doctor_profile_id} doesn't meet fee requirements")
            #     continue
            
            # Check if doctor has available time slots
            availabilities = [
                (_ensure_timezone_aware(a.start_time), _ensure_timezone_aware(a.end_time))
                for a in doctor.relevant_availability
            ]
            
            appointments = [
                (_ensure_timezone_aware(b.start_time), _ensure_timezone_aware(b.end_time))
                for b in doctor.relevant_appointments
            ]
            
            total_available_minutes = 0
            available_slots = []
            
            # Calculate available time by subtracting appointments from availability
            for avail_start, avail_end in availabilities:
                # Constrain to target date range
                constrained_start = max(avail_start, start_time)
                constrained_end = min(avail_end, end_time)
                
                if constrained_start >= constrained_end:
                    continue
                
                # Get free blocks for this availability period
                free_blocks = subtract_appointments_from_availability(
                    constrained_start, constrained_end, appointments
                )
                
                for block_start, block_end in free_blocks:
                    block_duration = int((block_end - block_start).total_seconds() / 60)
                    if block_duration >= 15:
                        total_available_minutes += block_duration
                        available_slots.append({
                            'start': block_start.isoformat(),
                            'end': block_end.isoformat(),
                            'duration_minutes': block_duration
                        })
            
            # If doctor has sufficient available time, add to results
            if total_available_minutes >= 15:
                # Get doctor languages
                languages = [
                    lang.language.language for lang in doctor.known_languages.all()
                ] if hasattr(doctor, 'known_languages') else []
                
                # Get doctor specializations
                specializations = [
                    spec.specialization.specialization
                    for spec in doctor.doctor_specializations.all()
                ]
                
                # A placeholder for fee since the original logic was commented out
                doctor_fee = 0 
                
                doctor_info = {
                    'doctor_id': doctor.doctor_profile_id,
                    'name': f"{doctor.first_name} {doctor.last_name}".strip(),
                    'total_available_minutes': total_available_minutes,
                    'fee': doctor_fee # Placeholder; replace with actual fee logic
                }
                
                available_doctors.append(doctor_info)
        
        # Sort doctors by total available time (descending) and then by fee (ascending)
        available_doctors.sort(key=lambda x: (-x['total_available_minutes'], x['fee']))
        
        logger.info(f"Found {len(available_doctors)} available doctors for specialization {specialization_id}")
        
        return available_doctors if available_doctors else None
        
    # except Exception as e:
    #     logger.error(f"Error in get_available_doctors_for_specialization: {e}")
    #     return None


# Helper function (reusing from your existing code)
def _ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware"""
    if dt.tzinfo is None:
        return django_timezone.make_aware(dt)
    return dt










from django.utils import timezone 

def is_doctor_available_in_specialization(specialization_id, days, country):
    start_time = timezone.now()
    end_time = start_time + timedelta(days=days)

    available_doctors = get_available_doctors_for_specialization(
        specialization_id=specialization_id,
        start_time=start_time,
        end_time=end_time,
        country=country
    )
    if available_doctors:
        return True
    return False

from administrator.models import Specializations
from ..serializers import SpecializationsSerializerFull

def get_specializations_service(country):
    specializations = Specializations.objects.exclude(specialization='No Specialization')
    serializer = SpecializationsSerializerFull(specializations, many=True)
    specializations_data = serializer.data
    for specialization in specializations_data:
        specialization['is_doctor_available'] = is_doctor_available_in_specialization(specialization['specialization_id'], 180, country)
    return specializations_data
