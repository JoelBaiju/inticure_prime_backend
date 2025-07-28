# services/slot_generator.py
from datetime import timedelta, datetime, time
from collections import defaultdict

from django.utils import timezone
from django.db.models import Q

from .models import DoctorAvailableHours, DoctorAppointment, DoctorSpecializations, Specializations, DoctorProfiles, Calendar, LanguagesKnown
from general.models import UserPreferredDoctors

def subtract_appointments_from_availability(availability_start, availability_end, appointments):
    appointments = sorted(appointments, key=lambda x: x[0])
    free_blocks = []
    current_start = availability_start

    for appt_start, appt_end in appointments:
        if current_start < appt_start:
            free_blocks.append((current_start, appt_start))
        current_start = max(current_start, appt_end)

    if current_start < availability_end:
        free_blocks.append((current_start, availability_end))

    return free_blocks

def generate_clean_slots(free_blocks, session_duration, alignment_minutes):
    clean_slots = []
    duration_td = timedelta(minutes=session_duration)
    break_td = timedelta(minutes=5)
    total_required = duration_td + break_td

    for block_start, block_end in free_blocks:
        aligned_start = block_start

        # If alignment is same as session_duration, skip aligning step
        if alignment_minutes != session_duration:
            if aligned_start.minute % alignment_minutes != 0:
                aligned_minute = (aligned_start.minute // alignment_minutes + 1) * alignment_minutes
                aligned_start = aligned_start.replace(minute=0) + timedelta(minutes=aligned_minute)
                if aligned_start < block_start:
                    aligned_start += timedelta(minutes=alignment_minutes)

        while aligned_start + total_required <= block_end:
            slot = (aligned_start, aligned_start + duration_td)
            clean_slots.append(slot)
            aligned_start += duration_td + break_td  # Move by session + break

    return clean_slots



def get_preferred_doctors(gender_info, language_info, flag, country, specialization, is_couple):
    gender = gender_info.get('value') if gender_info else None
    gender_priority = int(gender_info.get('priority', 0)) if gender_info else 0
    language = language_info.get('value') if language_info else None
    language_priority = int(language_info.get('priority', 0)) if language_info else 0

    q_gender = Q(gender=gender) if gender else Q()
    q_language = Q(known_languages__language__language__iexact=language) if language else Q()

    # Initial query
    doctors = DoctorProfiles.objects.filter(
        doctor_flag=flag,
        is_accepted=True,
        payment_assignments__country__country_name=country,
        payment_assignments__specialization=specialization,
    ).distinct()

    # Filter based on effective payment
    filtered_doctors = []
    for doctor in doctors:
        for rule in doctor.payment_assignments.filter(
            country__country_name=country,
            specialization=specialization
        ):
            effective_payment = rule.get_effective_payment()
            if is_couple:
                if effective_payment.get("custom_doctor_fee_couple", 0) > 2:
                    filtered_doctors.append(doctor.doctor_profile_id)
                    break
            else:
                if effective_payment.get("custom_doctor_fee_single", 0) > 2:
                    filtered_doctors.append(doctor.doctor_profile_id)
                    break

    # Convert list of doctor IDs to a QuerySet
    if filtered_doctors:
        doctors = DoctorProfiles.objects.filter(doctor_profile_id__in=filtered_doctors)
    else:
        doctors = DoctorProfiles.objects.none()

    # Preference filtering
    gender_matched = False
    language_matched = False
    fallback_reason = None
    preferred_doctors = DoctorProfiles.objects.none()

    if gender and language:
        preferred_doctors = doctors.filter(q_gender & q_language).distinct()
        if preferred_doctors.exists():
            gender_matched = True
            language_matched = True
        else:
            if gender_priority >= language_priority:
                preferred_doctors = doctors.filter(q_gender).distinct()
                if preferred_doctors.exists():
                    gender_matched = True
                    fallback_reason = "No doctors matched both preferences, fallback to gender only"
                else:
                    preferred_doctors = doctors.filter(q_language).distinct()
                    if preferred_doctors.exists():
                        language_matched = True
                        fallback_reason = "No doctors matched gender, fallback to language only"
            else:
                preferred_doctors = doctors.filter(q_language).distinct()
                if preferred_doctors.exists():
                    language_matched = True
                    fallback_reason = "No doctors matched both preferences, fallback to language only"
                else:
                    preferred_doctors = doctors.filter(q_gender).distinct()
                    if preferred_doctors.exists():
                        gender_matched = True
                        fallback_reason = "No doctors matched language, fallback to gender only"

    elif gender:
        preferred_doctors = doctors.filter(q_gender).distinct()
        if preferred_doctors.exists():
            gender_matched = True

    elif language:
        preferred_doctors = doctors.filter(q_language).distinct()
        if preferred_doctors.exists():
            language_matched = True

    else:
        preferred_doctors = doctors
        fallback_reason = "No preferences provided, showing all doctors"

    preferred_doctor_ids = list(preferred_doctors.values_list("doctor_profile_id", flat=True))

    return preferred_doctors, preferred_doctor_ids, gender_matched, language_matched, fallback_reason





















def generate_slots_for_doctors(doctors_queryset, target_date , session_duration , alignment_minutes):
    temp_slot_pool = defaultdict(list)
    for doctor in doctors_queryset:
        try:
            calendar_entry = Calendar.objects.get(date=target_date)
        except Calendar.DoesNotExist:
            continue

        availabilities = DoctorAvailableHours.objects.filter(
            doctor=doctor,
            date=calendar_entry
        )

        free_blocks = []
        for availability in availabilities:
            block_start = timezone.make_aware(datetime.combine(target_date, availability.start_time))
            block_end = timezone.make_aware(datetime.combine(target_date, availability.end_time))
            free_blocks.append((block_start, block_end))

        appointments_qs = DoctorAppointment.objects.filter(
            doctor=doctor,
            date=calendar_entry
        )
        appointments = [
            (
                timezone.make_aware(datetime.combine(target_date, a.start_time)),
                timezone.make_aware(datetime.combine(target_date, a.end_time))
            ) for a in appointments_qs
        ]

        for block_start, block_end in free_blocks:
            clean_blocks = subtract_appointments_from_availability(block_start, block_end, appointments)
            clean_slots = generate_clean_slots(clean_blocks, session_duration, alignment_minutes)
            for slot in clean_slots:
                key = (slot[0].time(), slot[1].time())
                temp_slot_pool[key].append(doctor.doctor_profile_id)
    return temp_slot_pool






def get_available_slots(specialization_id=None, date=None, is_couple=False,
                        alignment_minutes=None, is_junior=False,
                        gender_info=None, language_info=None,
                        specialization='No Specialization', country=None,
                        doctor_id=None):
    session_duration = 15 if is_junior else None
    doctors = []
    fallback_reason = None
    doctors_found_but_unavailable = False
    gender_matched = False
    language_matched = False

    # Case 1: doctor_id is provided — direct slot generation
    if doctor_id:
        try:
            doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
            doctors = [doctor]
            is_junior = doctor.doctor_flag == 'junior'
            if not is_junior:
                specialization = doctor.doctor_specializations.first().specialization.specialization if doctor.doctor_specializations.exists() else 'No Specialization'
                spec_obj = doctor.doctor_specializations.first().specialization
                session_duration_field = spec_obj.double_session_duration if is_couple else spec_obj.single_session_duration
                if session_duration_field is None:
                    return []

                session_duration = int(session_duration_field.total_seconds() // 60)
            else:
                session_duration = 15  # For junior, fallback to default

        except DoctorProfiles.DoesNotExist:
            return {"error": "Doctor not found"}

        if alignment_minutes is None:
            alignment_minutes = 20

        slot_pool = generate_slots_for_doctors(doctors, date, session_duration, alignment_minutes)

        formatted_slots = [
            {
                "start": key[0].isoformat(),
                "end": key[1].isoformat(),
                "available_doctors": doctor_ids
            } for key, doctor_ids in slot_pool.items()
        ]

        available_dates = []
        date_cursor = date
        for _ in range(14):
            temp_pool = generate_slots_for_doctors(doctors, date_cursor, session_duration, alignment_minutes)
            if temp_pool:
                available_dates.append(str(date_cursor))
            date_cursor += timedelta(days=1)

        return {
            "slots": formatted_slots,
            "matched_preferences": True,  # directly matched by ID
            "gender_matched": True,
            "language_matched": True,
            "fallback_reason": None,
            "doctors_found_but_unavailable": not formatted_slots,
            "available_dates": available_dates
        }

    # Case 2: doctor_id not provided — proceed with filtering logic
    if is_junior:
        specialization = Specializations.objects.get(specialization_id=specialization_id)
        doctors, _, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
            gender_info, language_info, flag="junior", country=country, specialization=specialization , is_couple = is_couple
        )
    else:
        specialization = Specializations.objects.get(specialization_id=specialization_id)
        session_duration_field = specialization.double_session_duration if is_couple else specialization.single_session_duration

        if session_duration_field is None:
            return []

        session_duration = int(session_duration_field.total_seconds() // 60)

        doctor_specs = DoctorSpecializations.objects.filter(specialization=specialization)
        all_senior_doctors = DoctorProfiles.objects.filter(
            doctor_flag="senior",
            doctor_specializations__in=doctor_specs
        ).distinct()

        doctors, _, gender_matched, language_matched, fallback_reason = get_preferred_doctors(
            gender_info, language_info, flag="senior", country=country, specialization=specialization ,is_couple=is_couple
        )
        doctors = doctors.filter(doctor_specializations__in=doctor_specs).distinct()

        if not doctors.exists():
            doctors = all_senior_doctors
            fallback_reason = "No preferred doctors matched specialization, falling back to all with specialization"
            gender_matched = False
            language_matched = False

    if alignment_minutes is None:
        alignment_minutes = 20

    slot_pool = generate_slots_for_doctors(doctors, date, session_duration, alignment_minutes)

    formatted_slots = [
        {
            "start": key[0].isoformat(),
            "end": key[1].isoformat(),
            "available_doctors": doctor_ids
        } for key, doctor_ids in slot_pool.items()
    ]

    if not formatted_slots and doctors.exists():
        doctors_found_but_unavailable = True

    available_dates = []
    date_cursor = date
    for _ in range(14):
        temp_pool = generate_slots_for_doctors(doctors, date_cursor, session_duration, alignment_minutes)
        if temp_pool:
            available_dates.append(str(date_cursor))
        date_cursor += timedelta(days=1)

    if not formatted_slots:
        fallback_reason = fallback_reason or "No available slots with preferred doctors. Showing all available slots."
        if not is_junior:
            doctors = DoctorProfiles.objects.filter(
                doctor_flag="senior",
                is_accepted=True,
                doctor_specializations__in=doctor_specs
            ).distinct()
        else:
            doctors = DoctorProfiles.objects.filter(
                doctor_flag='junior',
                is_accepted=True,
                payment_assignments__country__country_name=country,
            ).distinct()

        slot_pool.clear()
        slot_pool = generate_slots_for_doctors(doctors, date, session_duration, alignment_minutes)

        formatted_slots = [
            {
                "start": key[0].isoformat(),
                "end": key[1].isoformat(),
                "available_doctors": doctor_ids
            } for key, doctor_ids in slot_pool.items()
        ]

    return {
        "slots": formatted_slots,
        "matched_preferences": gender_matched or language_matched,
        "gender_matched": gender_matched,
        "language_matched": language_matched,
        "fallback_reason": fallback_reason,
        "doctors_found_but_unavailable": doctors_found_but_unavailable,
        "available_dates": available_dates
    }
