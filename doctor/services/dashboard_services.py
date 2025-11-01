from datetime import timedelta
from django.db.models import Sum, Q
from django.utils import timezone

from ..models import DoctorProfiles, DoctorAppointment
from analysis.models import AppointmentHeader
from general.models import PreTransactionData
from general.utils import convert_utc_to_local_return_dt


def get_doctor_or_none(user):
    try:
        return DoctorProfiles.objects.get(user=user)
    except DoctorProfiles.DoesNotExist:
        return None


def get_earnings(doctor):
    """Compute earnings today, yesterday, and percentage change."""
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    earnings_today_total = PreTransactionData.objects.filter(
        appointment__doctor=doctor,
        appointment__start_time__date=today,
        appointment__completed = True
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    earnings_today_vendor = PreTransactionData.objects.filter(
        appointment__doctor=doctor,
        appointment__start_time__date=today,
        appointment__completed = True
    ).aggregate(total=Sum("vendor_fee"))["total"] or 0

    earnings_today = earnings_today_total - earnings_today_vendor

    earnings_yesterday_total = PreTransactionData.objects.filter(
        appointment__doctor=doctor,
        appointment__start_time__date=yesterday
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    earnings_yesterday_vendor = PreTransactionData.objects.filter(
        appointment__doctor=doctor,
        appointment__start_time__date=yesterday
    ).aggregate(total=Sum("vendor_fee"))["total"] or 0

    earnings_yesterday = earnings_yesterday_total - earnings_yesterday_vendor

    earnings_change = (
        round(((earnings_today - earnings_yesterday) / earnings_yesterday) * 100, 2)
        if earnings_yesterday > 0 else 0.0
    )

    return {
        "earnings_today": earnings_today,
        "earnings_change": earnings_change
    }

from general.utils import get_today_start_end_for_doctor_tz

def get_today_appointments(doctor):
    """Return today’s appointments summary (total, completed, pending)."""

    start , end = get_today_start_end_for_doctor_tz(doctor.time_zone)

    appointments_today_qs = DoctorAppointment.objects.filter(
        doctor=doctor,
        confirmed=True,
        start_time__gte=start,
        start_time__lte=end
    )

    total = appointments_today_qs.count()
    completed = appointments_today_qs.filter(completed=True).count()
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }


def get_doctor_info(doctor):
    """Return formatted doctor profile info."""
    specialization_qs = doctor.doctor_specializations.all()
    specialization_names = ", ".join(
        [spec.specialization.specialization for spec in specialization_qs]
    ) if specialization_qs else "no specialization"
    return {
        "name": f"{doctor.salutation} {doctor.first_name} {doctor.last_name}",
        "salutaion": doctor.salutation ,
        "first_name":doctor.first_name ,
        "last_name": doctor.last_name ,
        "specialization": specialization_names,
        "experience": doctor.experience if doctor.experience else "N/A",
        "rating": 4.9,  # TODO: Replace placeholder
        "email": doctor.email_id,
        "bio":doctor.doctor_bio,
        "profile_pic":doctor.profile_pic.url,
        "address":doctor.address,
        "gender":doctor.gender,
        "reg_year":doctor.registration_year ,
        "dob" :doctor.dob,  
        "whatsapp_number":doctor.whatsapp_number, 
        "qualification":doctor.qualification ,
        "time_zone": doctor.time_zone,
    }


def get_upcoming_appointments(doctor, limit=3):
    """Return a list of upcoming confirmed appointments."""
    now = timezone.now()
    today = now.date()

    upcoming_qs = AppointmentHeader.objects.filter(
        doctor=doctor,
        appointment_status="confirmed",
        completed=False
    ).filter(
        Q(end_time__gte=now) | Q(start_time__date__gt=today)
    ).order_by("start_time")[:limit]

    upcoming = []
    for appt in upcoming_qs:
        customer_name = (
            f"{appt.customer.user.first_name} {appt.customer.user.last_name}"
            if appt and appt.customer else "Unknown"
        )
        appt_type = "Couple" if appt and appt.is_couple else "Individual"
        time_str = convert_utc_to_local_return_dt(appt.start_time, doctor.time_zone).time()

        if appt.start_time and appt.end_time:
            duration_minutes = int((appt.end_time - appt.start_time).total_seconds() // 60)
            duration = f"{duration_minutes} mins"
        else:
            duration = "Unknown"

        specialization_name = appt.specialization.specialization if appt.specialization else "General"

        upcoming.append({
            "appointment_id": appt.appointment_id,
            "name": customer_name,
            "type": appt_type,
            "time": time_str,
            "duration": duration,
            "specialization": specialization_name,
            "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
            "followup": bool(appt.followup),
            "meeting_link": appt.meeting_link,
            "date": convert_utc_to_local_return_dt(appt.start_time, doctor.time_zone).date(),
            "status": appt.appointment_status
        })
    return upcoming


def build_dashboard_response(doctor):
    """Aggregate all dashboard data into one response dict."""
    return {
        **get_earnings(doctor),
        "appointments_today": get_today_appointments(doctor),
        "doctor_info": get_doctor_info(doctor),
        "upcoming_appointments": get_upcoming_appointments(doctor),
    }
