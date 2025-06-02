
from administrator.models import Plans

def first_consultation_cost_calculator(appointment):
    doctor_fee = appointment.appointment_slot.doctor.doctor_payment_rate.rate_per_session
    platform_fee = Plans.objects.get(name = 'default_plan').price
    total_cost = doctor_fee + platform_fee
    return {
        'doctor_fee': doctor_fee,
        'platform_fee': platform_fee,
        'total_cost': total_cost
    }

