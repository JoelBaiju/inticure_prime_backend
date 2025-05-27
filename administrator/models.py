from django.db import models
# from analysis.models import *
# from doctor.models import DoctorDoctorProfiles
# # Create your models here.

# class AdministratorCouponRedeemLog(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     coupon = models.ForeignKey('AdministratorDiscountCoupons', on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'administrator_couponredeemlog'

# class AdministratorDiscountCoupons(models.Model):
#     coupon_code = models.CharField(max_length=60, null=True)
#     discount_percentage = models.IntegerField(null=True)
#     expiry_date = models.DateField(null=True)

#     class Meta:
#         db_table = 'administrator_discountcoupons'

# class AdministratorDuration(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     duration = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'administrator_duration'

# class AdministratorInticureEarnings(models.Model):
#     net_profit = models.BigIntegerField(null=True)
#     net_expense = models.BigIntegerField(null=True)
#     net_income = models.BigIntegerField(null=True)
#     net_amount = models.BigIntegerField(null=True)
#     net_amount_usd = models.BigIntegerField()
#     net_expense_usd = models.BigIntegerField()
#     net_income_usd = models.BigIntegerField()
#     net_profit_usd = models.BigIntegerField()
#     currency = models.CharField(max_length=10, null=True)

#     class Meta:
#         db_table = 'administrator_inticureearnings'

# class AdministratorLanguagesKnown(models.Model):
#     language = models.TextField(null=True)

#     class Meta:
#         db_table = 'administrator_languagesknown'

class AdministratorLocations(models.Model):
    location = models.CharField(max_length=20)
    currency = models.CharField(max_length=10)
    country_code = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'administrator_locations'

# class AdministratorPayouts(models.Model):
#     payout_date = models.DateField()
#     payout_time = models.TimeField()
#     accepted_date = models.DateField(null=True)
#     accepted_time = models.TimeField(null=True)
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     payout_status = models.IntegerField()
#     payout_amount = models.IntegerField(null=True)
#     appointment = models.ForeignKey('AnalysisAppointmentHeader', on_delete=models.SET_NULL, null=True)
#     doctor_name = models.CharField(max_length=30, null=True)
#     base_amount = models.IntegerField(null=True)
#     inticure_fee = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'administrator_payouts'

# class AdministratorPlans(models.Model):
#     price = models.IntegerField(null=True)
#     specialization = models.CharField(max_length=50, null=True)
#     location = models.ForeignKey(AdministratorLocations, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'administrator_plans'

# class AdministratorReportCustomer(models.Model):
#     appointment = models.ForeignKey('AnalysisAppointmentHeader', on_delete=models.SET_NULL, null=True)
#     customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_customers')
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     report_remarks = models.TextField(null=True)
#     report_count = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'administrator_reportcustomer'

# class AdministratorSpecializationTimeDuration(models.Model):
#     specialization = models.CharField(max_length=50, null=True)
#     time_duration = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'administrator_specializationtimeduration'

# class AdministratorTotalEarnings(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.CASCADE)
#     accepted_date = models.DateField(null=True)
#     accepted_time = models.TimeField(null=True)
#     total_earnings = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'administrator_totalearnings'

# class AdministratorTotalPayouts(models.Model):
#     payout_date = models.DateField()
#     payout_time = models.TimeField()
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     total_payouts = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'administrator_totalpayouts'

# class AdministratorTransactions(models.Model):
#     invoice = models.ForeignKey('AnalysisInvoices', on_delete=models.SET_NULL, null=True)
#     transaction_amount = models.IntegerField(null=True)
#     transaction_date = models.DateField()
#     transaction_time = models.TimeField()
#     payment_status = models.IntegerField()

#     class Meta:
#         db_table = 'administrator_transactions'

