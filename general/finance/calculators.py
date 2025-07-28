
from analysis.models import AppointmentHeader
from decimal import Decimal
from administrator.models import PaymentEntries
from doctor.models import DoctorPaymentRules
from analysis.models import AppointmentHeader

def first_consultation_cost_calculator(appointment_id):
    obj = first_consultation_cost_calculator_2(appointment_id)
    return {
        'doctor_fee': obj.doctor_share,
        'platform_fee': obj.inticure_share,
        'total_cost': obj.total_amount
    }

def first_consultation_cost_calculator_2(appointment_id):
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

    doctor = appointment.doctor
    country = appointment.customer.country_details
    specialization = appointment.specialization
    session_count = 1  # assuming always 1 for first consultation
    appointment_type = appointment.type_booking or "single"
    print(doctor , country , specialization , session_count , appointment_type)
    try:
        payment_rule = DoctorPaymentRules.objects.get(
            doctor=doctor,
            country=country,
            specialization=specialization,
            session_count=session_count
        )
    except DoctorPaymentRules.DoesNotExist:
        raise Exception(f"No payment rule found for doctor {doctor.first_name}, country {country.country_name}, specialization {specialization if specialization else 'None'}, session count {session_count}")

    payment_data = payment_rule.get_effective_payment()

    if appointment_type == "couple":
        doctor_fee = Decimal(payment_data["custom_doctor_fee_couple"])
        user_total = Decimal(payment_data["custom_user_total_fee_couple"])
    else:
        doctor_fee = Decimal(payment_data["custom_doctor_fee_single"])
        user_total = Decimal(payment_data["custom_user_total_fee_single"])

    inticure_share = user_total - doctor_fee

    payment_obj, created = PaymentEntries.objects.get_or_create(appointment=appointment)
    payment_obj.total_amount = user_total
    payment_obj.doctor_share = doctor_fee
    payment_obj.inticure_share = inticure_share
    payment_obj.doctor_base_rate = doctor_fee
    payment_obj.country_base_rate = user_total
    payment_obj.inticure_share_from_min_percent = Decimal("0.00")  # optional logic
    payment_obj.inticure_share_from_country_diff = Decimal("0.00")  # optional logic
    payment_obj.inticure_min_percent = Decimal("0.00")  # optional logic
    payment_obj.save()

    return payment_obj
