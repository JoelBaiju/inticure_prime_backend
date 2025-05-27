from django.db import models
from django.contrib.auth.models import User
from analysis.models import *
from administrator.models import *
# Create your models here.



# # Customer Models
# class AppointmentRatings(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     rating_comments = models.TextField(null=True)
#     rating = models.IntegerField(null=True)
#     app_rating = models.IntegerField(null=True)
#     added_by = models.CharField(max_length=25)

#     class Meta:
#         db_table = 'customer_appointmentratings'

class CustomerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    mobile_number = models.BigIntegerField(null=True)
    address = models.CharField(max_length=50, null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=20, null=True)
    location = models.ForeignKey(AdministratorLocations, on_delete=models.SET_NULL, null=True)
    other_gender = models.CharField(max_length=20, null=True)
    profile_pic = models.TextField(null=True)

    class Meta:
        db_table = 'customer_customerprofile'

# class RazorpayCustomer(models.Model):
#     razorpay_customer_token_id = models.TextField()
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'customer_razorpaycustomer'

# class Refund(models.Model):
#     refund_id = models.CharField(max_length=50)
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     refund_status = models.IntegerField()
#     refund_requested_date = models.DateField()
#     refund_processed_date = models.DateField(null=True)
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     appointment_date = models.DateField()
#     refund_amount = models.IntegerField()

#     class Meta:
#         db_table = 'customer_refund'

# class StripeCustomer(models.Model):
#     stripe_customer_token_id = models.TextField()
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'customer_stripecustomer'

# class TemporaryTransactionData(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     currency = models.CharField(max_length=10, null=True)
#     total_amount = models.IntegerField(null=True)
#     discount = models.IntegerField(null=True)
#     coupon = models.ForeignKey(AdministratorDiscountCoupons, on_delete=models.SET_NULL, null=True)
#     tax = models.IntegerField(null=True)
#     vendor_fee = models.IntegerField(null=True)
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'customer_temporarytransactiondata'
