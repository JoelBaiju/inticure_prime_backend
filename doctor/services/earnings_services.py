# services/earnings.py
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from general.models import  PreTransactionData
from administrator.models import PaymentEntries
from doctor.models import Payouts,Doctor_Bank_Account

from doctor.models import DoctorProfiles


def mask_account_number(account_number: str) -> str:
    """Masks an account number, keeping only first 4 and last 4 digits visible."""
    return ''.join([*account_number[:4], '*' * (len(account_number) - 8), *account_number[-4:]])


def get_doctor_earnings(user):
    """Return full earnings dashboard for a doctor user."""
    doctor = DoctorProfiles.objects.get(user=user)

    # Completed payments → wallet balance
    payments = PaymentEntries.objects.filter(
        appointment__doctor=doctor,
        appointment__completed=True,
    )
    total_earnings = sum(payment.doctor_share for payment in payments)

    today = timezone.now().date()

    # Monthly aggregates
    total_earnings_this_month = (
        PreTransactionData.objects.filter(
            appointment__doctor=doctor,
            appointment__start_time__date__gte=timezone.now().replace(day=1),
            appointment__start_time__date__lte=timezone.now(),
            appointment__completed = True
        ).aggregate(Sum("total_amount"))["total_amount__sum"]
        or 0
    )

    total_earnings_last_month = (
        PreTransactionData.objects.filter(
            appointment__doctor=doctor,
            appointment__start_time__date__gte=timezone.now().replace(month=timezone.now().month - 1, day=1),
            appointment__completed = True,
            appointment__start_time__date__lte=timezone.now().replace(day=1) - timedelta(days=1),
        ).aggregate(Sum("total_amount"))["total_amount__sum"]
        or 0
    )

    # Growth %
    earnings_growth = (
        (total_earnings_this_month - total_earnings_last_month) / total_earnings_last_month * 100
        if total_earnings_last_month
        else 0
    )

    average_earning_per_day = total_earnings_this_month / timezone.now().day

    # This week's daily earnings (only non-zero days)
    this_weeks_earnings_per_day = []
    for i in range(7):
        date_obj = today - timedelta(days=i)
        earnings = (
            PreTransactionData.objects.filter(
                appointment__doctor=doctor,
                appointment__start_time__date=date_obj,
                appointment__completed = True
            ).aggregate(total=Sum("total_amount"))["total"]
            or 0
        )
        if earnings > 0:
            this_weeks_earnings_per_day.append(
                {
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "day": date_obj.strftime("%A"),
                    "earnings": earnings,
                    "progress_compared_to_average": (
                        (earnings - average_earning_per_day) / average_earning_per_day * 100
                        if average_earning_per_day
                        else 0
                    ),
                }
            )

    # Payouts and wallet balance
    total_payouts = doctor.payouts.aggregate(Sum("amount"))["amount__sum"] or 0
    wallet_balance = total_earnings - total_payouts

    # Next payout in queue
    next_payout = (
        Payouts.objects.filter(doctor=doctor, status="processing")
        .order_by("initiated_at")
        .first()
    )

    # Bank account details
    bank_account = Doctor_Bank_Account.objects.filter(doctor=doctor).first()
    if bank_account:
        account_number = mask_account_number(bank_account.account_number)
        account_holder_name = bank_account.account_holder_name
    else:
        account_number = None
        account_holder_name = None

    return {
        "total_earnings": total_earnings,
        "total_earnings_this_month": total_earnings_this_month,
        "total_earnings_last_month": total_earnings_last_month,
        "earnings_growth_this_month_compared_to_last_month": earnings_growth,
        "average_earning_per_day": average_earning_per_day,
        "this_weeks_earnings_per_day": this_weeks_earnings_per_day,
        "total_payouts": total_payouts,
        "wallet_balance": wallet_balance,
        "next_payout_amount": next_payout.amount if next_payout else 0,
        "next_payout_date": next_payout.initiated_at if next_payout else None,
        "bank_account_exists": bool(bank_account),
        "doctor_id": doctor.doctor_profile_id,
        "account_number": account_number,
        "account_holder_name": account_holder_name,
    }
