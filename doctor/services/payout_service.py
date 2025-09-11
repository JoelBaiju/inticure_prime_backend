from django.db.models import Sum
from django.utils import timezone
from doctor.models import DoctorProfiles, Payouts, PaymentEntries

def calculate_wallet_balance(doctor):
    payments = PaymentEntries.objects.filter(
        appointment__doctor=doctor,
        appointment__completed=True,
    )
    total_earnings = sum(payment.doctor_share for payment in payments)
    total_payouts = doctor.payouts.aggregate(Sum('amount'))['amount__sum'] or 0
    return total_earnings - total_payouts


def create_payout(doctor, amount):
    # Prevent duplicate processing payouts
    existing_payout = Payouts.objects.filter(doctor=doctor, status='processing').first()
    if existing_payout:
        raise Exception("Existing payout is processing")

    wallet_balance = calculate_wallet_balance(doctor)

    if wallet_balance < 0:
        raise Exception("Insufficient balance")

    if float(amount) > wallet_balance:
        raise Exception("Insufficient balance")

    payout = Payouts.objects.create(
        doctor=doctor,
        amount=float(amount),
        initiated_at=timezone.now(),
        status='processing',
    )
    return payout
