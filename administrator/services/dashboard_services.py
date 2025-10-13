from doctor.models import *
from analysis.models import *
from customer.models import *
from general.models import PreTransactionData
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta



def get_revenue():
    """Compute earnings today, yesterday, and percentage change."""
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    earnings_today = PreTransactionData.objects.filter(
        appointment__start_time__date=today,
        appointment__completed = True
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    earnings_yesterday = PreTransactionData.objects.filter(
        appointment__start_time__date=yesterday
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    earnings_change = (
        round(((earnings_today - earnings_yesterday) / earnings_yesterday) * 100, 2)
        if earnings_yesterday > 0 else 0.0
    )

    return {
        "today_revenue": earnings_today,
        "rvenue_change": earnings_change,
        "yesterday_revenue": earnings_yesterday
    }

def get_patient_count():
    total_count = CustomerProfile.objects.count()
    patients_today = CustomerProfile.objects.filter(
                user__date_joined__date=timezone.now().date()
            ).count()
    male_patients = CustomerProfile.objects.filter(gender='Male').count()
    female_patients = CustomerProfile.objects.filter(gender ='Female').count()
    return {
        "patients_total": total_count,
        "patients_today": patients_today,
        "male_patients": male_patients,
        "female_patients":  female_patients 
    }


def appointments_coount():
    today = timezone.now().date()
    todays_count = AppointmentHeader.objects.filter(
        start_time__date=today
    ).count()
    upcoming_count = AppointmentHeader.objects.filter(
        start_time__date__gt=today
    ).count()
    return {
        "todays_appointments": todays_count,
        "upcoming_appointments": upcoming_count
    }


def doctor_count():
    total_count = DoctorProfiles.objects.filter(is_accepted=True).count()
    male_doctors = DoctorProfiles.objects.filter(gender='Male', is_accepted=True).count()
    female_doctors = DoctorProfiles.objects.filter(gender='Female', is_accepted=True).count()
    junior_doctors = DoctorProfiles.objects.filter(doctor_flag='junior', is_accepted=True).count()
    senior_doctors = DoctorProfiles.objects.filter(doctor_flag='senior', is_accepted=True).count()
    return {
        "doctors_total": total_count,
        "male_doctors": male_doctors,
        "female_doctors": female_doctors,
        "junior_doctors": junior_doctors,
        "senior_doctors": senior_doctors       
        }


def get_dashboard_data():
    data = {}
    data['doctors'] = doctor_count()
    data['patients'] = get_patient_count()
    data['total_appointments'] = AppointmentHeader.objects.count()
    data['revenue'] = get_revenue()
    data['appointments'] = appointments_coount()
    return data