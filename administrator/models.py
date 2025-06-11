from pyexpat import model
from django.db import models


# Create your models here.
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
    
class Plans(models.Model):
    name=models.CharField(max_length=50, null=True)
    description=models.TextField(null=True)
    price=models.IntegerField(null=True)
    specialization=models.CharField(null=True,max_length=50)
    location_id=models.IntegerField(default=0)
    number_of_sessions=models.IntegerField(null=True)

class Countries(models.Model):
    country_name=models.CharField(max_length=20)
    representation=models.CharField(max_length=20,null=True)
    currency=models.CharField(max_length=10)
    country_code=models.CharField(max_length=10,null=True)

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

class Transactions(models.Model):
    transaction_id=models.BigAutoField(primary_key=True)
    invoice_id=models.IntegerField(null=True)
    transaction_amount=models.IntegerField(null=True)
    transaction_date=models.DateField(auto_now=True)
    transaction_time=models.TimeField(auto_now=True)
    payment_status=models.IntegerField(default=0)


class ReportCustomer(models.Model):
    appointment_id=models.IntegerField(null=True)
    customer_id=models.IntegerField(null=True)
    doctor_id=models.IntegerField(null=True)
    report_remarks=models.TextField(null=True)
    report_count=models.IntegerField(null=True)
class SpecializationTimeDuration(models.Model):
    specialization_id=models.BigAutoField(primary_key=True)
    specialization=models.CharField(null=True,max_length=50)
    time_duration=models.IntegerField(null=True)
class DiscountCoupons(models.Model):
    coupon_code=models.CharField(null=True,max_length=60)
    discount_percentage=models.IntegerField(null=True)
    expiry_date=models.DateField(null=True)
class CouponRedeemLog(models.Model):
    user_id=models.IntegerField(null=True)
    coupon_id=models.IntegerField(null=True)
    