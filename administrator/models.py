from pyexpat import model
from django.db import models


class InticureEarnings(models.Model):
    net_profit=models.BigIntegerField(null=True)
    net_expense=models.BigIntegerField(null=True)
    net_income=models.BigIntegerField(null=True)
    net_amount=models.BigIntegerField(null=True)
    net_profit_usd=models.BigIntegerField(default=0)
    net_expense_usd=models.BigIntegerField(default=0)
    net_income_usd=models.BigIntegerField(default=0)
    net_amount_usd=models.BigIntegerField(default=0)
    currency=models.CharField(null=True,max_length=10)
    
class Countries(models.Model):
    country_name=models.CharField(max_length=20)
    representation=models.CharField(max_length=20,null=True)
    currency=models.CharField(max_length=10)
    currency_symbol = models.CharField(max_length=5 , null=True)
    country_code=models.CharField(max_length=10,null=True)

    def __str__(self):
        return self.country_name + " (" + self.representation + ") - " + self.currency + " (" + self.country_code + ")"

class LanguagesKnown(models.Model):
    language=models.TextField(null=True)
    
    def __str__(self):  
        return self.language

class Payouts(models.Model):
    payout_id=models.BigAutoField(primary_key=True)
    appointment_id=models.IntegerField(null=True)
    payout_date=models.DateField(auto_now=True)
    payout_time=models.TimeField(auto_now=True)
    accepted_date=models.DateField(null=True)
    accepted_time=models.TimeField(null=True)
    doctor_id=models.IntegerField(null=True)
    base_amount=models.IntegerField(null=True)
    inticure_fee=models.IntegerField(null=True)
    payout_status=models.IntegerField(default=0)
    payout_amount=models.IntegerField(null=True)
   
class TotalPayouts(models.Model):
    payout_date=models.DateField(auto_now=True)
    payout_time=models.TimeField(auto_now=True)
    doctor_id=models.IntegerField(null=True)
    total_payouts=models.IntegerField(null=True)

class TotalEarnings(models.Model): 
    doctor_id=models.BigIntegerField()
    accepted_date=models.DateField(null=True)
    accepted_time=models.TimeField(null=True)
    total_earnings=models.IntegerField(null=True)


class ReportCustomer(models.Model):
    appointment_id=models.IntegerField(null=True)
    customer_id=models.IntegerField(null=True)
    doctor_id=models.IntegerField(null=True)
    report_remarks=models.TextField(null=True)
    report_count=models.IntegerField(null=True)

class Specializations(models.Model):
    specialization_id=models.BigAutoField(primary_key=True)
    specialization=models.CharField(null=True,max_length=50)
    description = models.CharField(null=True,max_length=200)
    single_session_duration = models.DurationField(null=True, blank=True)
    double_session_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return str(self.specialization_id)+ " " + self.specialization
    
class DiscountCoupons(models.Model):
    coupon_code=models.CharField(null=True,max_length=60)
    discount_percentage=models.IntegerField(null=True)
    expiry_date=models.DateField(null=True)
class CouponRedeemLog(models.Model):
    user_id=models.IntegerField(null=True)
    coupon_id=models.IntegerField(null=True)
    









class Transactions(models.Model):
    transaction_id=models.BigAutoField(primary_key=True)
    invoice_id=models.IntegerField(null=True)
    transaction_amount=models.IntegerField(null=True)
    transaction_date=models.DateField(auto_now=True)
    transaction_time=models.TimeField(auto_now=True)
    payment_status=models.CharField(default="pending", max_length=20)



















class GeneralPaymentRules(models.Model):
    EXPERIENCE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    DOCTOR_FLAG_CHOICES = [
        ('junior', 'Junior'),
        ('senior', 'Senior'),
    ]

    pricing_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name or label for this pricing rule (e.g. 'Basic 1-Session India', '3-Session Plan')"
    )

    country                 = models.ForeignKey(Countries, on_delete=models.CASCADE, related_name='general_payment_rules')
    specialization          = models.ForeignKey(Specializations, on_delete=models.CASCADE, related_name='general_payment_rules')
    experience              = models.CharField(max_length=30, choices=EXPERIENCE_CHOICES, null=True)
    doctor_flag             = models.CharField(max_length=30, choices=DOCTOR_FLAG_CHOICES, null=True)
    session_count           = models.PositiveIntegerField(default=1, null=True, help_text="Number of sessions this rule applies to")

    doctor_fee_single       = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    user_total_fee_single   = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    doctor_fee_couple       = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    user_total_fee_couple   = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    actual_price_single     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_price_couple     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('country', 'specialization', 'experience', 'doctor_flag', 'session_count')

    def __str__(self):
        label = self.pricing_name or f"{self.specialization} | {self.country} | {self.session_count} sessions"
        return f"[General] {label}"











from decimal import Decimal
from django.db import models

class PaymentEntries(models.Model):
    payment_id = models.BigAutoField(primary_key=True)

    transaction = models.ForeignKey(
        Transactions, on_delete=models.CASCADE,
        related_name='payment_entries', null=True, blank=True
    )
    
    appointment = models.ForeignKey(
        "analysis.AppointmentHeader", on_delete=models.CASCADE,
        related_name='payment_entries', null=True, blank=True
    )

    # Core calculation values
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    doctor_share = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    inticure_share = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # Breakdown of logic
    doctor_base_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    country_base_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    inticure_share_from_min_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    inticure_share_from_country_diff = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    inticure_min_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00') , null=True)  # optional field for admin logic

    def __str__(self):
        return f"PaymentEntry #{self.payment_id} - Appointment #{self.appointment_id}"

