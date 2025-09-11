from django.db import models
from django.contrib.auth.models import User
from administrator.models import Countries

# Create your models here.
class CustomerProfile(models.Model):
    user                        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_profile')
    partner                     = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='partner_profile', null=True, blank=True)
    gender                      = models.CharField(max_length=20,blank=True, null=True)
    other_gender                = models.CharField(max_length=20,blank=True, null=True)
    address                     = models.CharField(max_length=50,blank=True, null=True)
    date_of_birth               = models.DateField(blank=True, null=True,auto_now_add=False)
    mobile_number               = models.CharField( max_length=20,blank=True, null=True)
    mob_country_code            = models.CharField( max_length=20,blank=True, null=True)
    email                       = models.CharField(max_length=100,blank=True, null=True)
    whatsapp_number             = models.CharField(max_length=20, blank=True, null=True)
    country_code                = models.CharField(max_length=5,null=True)
    country_details             = models.ForeignKey(Countries, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    profile_pic                 = models.TextField(null=True)
    completed_first_analysis    = models.BooleanField(default=False)
    preferred_name              = models.CharField(max_length=110,blank=True, null=True)
    weight                      = models.CharField(max_length=255, null=True, blank=True)
    weight_unit                 = models.CharField(max_length=20 , null=True )
    height                      = models.CharField(max_length=255, null=True, blank=True)
    height_unit                 = models.CharField(max_length=20 , null=True )
    time_zone                   = models.CharField(max_length=50, default='UTC', null=True, blank=True)
    stripe_customer_id          = models.CharField(max_length=255, null=True, blank=True)
    confirmation_method         = models.CharField(max_length=50 , null=True)
    guardian_first_name         = models.CharField(max_length=50 , null=True)
    guardian_last_name          = models.CharField(max_length=50 , null=True)
    guardian_relation           = models.CharField(max_length=50 , null=True)
    guardian_phone_number       = models.CharField(max_length=50 , null=True)



    def __str__(self):
        return f"{self.user.username} -{self.user.first_name}-{self.user.last_name}- {self.preferred_name if self.preferred_name else 'No Preferred Name'}"




class Extra_questions(models.Model):
    question    = models.CharField(max_length=255, null=True, blank=True)
    group       = models.CharField(max_length=20 , null=True)

    
class Extra_questions_answers(models.Model):
    question    = models.ForeignKey(Extra_questions, on_delete=models.CASCADE, related_name='extra_questions_answers')
    answer      = models.CharField(max_length=255, null=True, blank=True)
    customer    = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='extra_questions_answers')

class AppointmentRatings(models.Model):
    appointment_id   = models.BigIntegerField(null=True)
    doctor_id        = models.BigIntegerField(null=True)
    user_id          = models.BigIntegerField(null=True)
    rating_comments  = models.TextField(null=True)
    rating           = models.IntegerField(null=True)
    app_rating       = models.IntegerField(null=True)
    added_by         = models.CharField(max_length=25)


class Refund(models.Model):
    refund_amount   = models.IntegerField(null=True)
    refund_currency = models.CharField(max_length=10, null=True)
    refund_status   = models.CharField(max_length=255, null=True)
    appointment     = models.ForeignKey('analysis.AppointmentHeader', on_delete=models.CASCADE, related_name='refund' ,null=True)
    request_date    = models.DateTimeField(null=True)
    refund_date     = models.DateTimeField(null=True)
    refund_method   = models.CharField(max_length=255, null=True)
    refund_account_number = models.CharField(max_length=255, null=True)
    refund_account_IFSC_code = models.CharField(max_length=255, null=True)
    stripe_refund_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_refund_id = models.CharField(max_length=255, null=True, blank=True)



class Customer_Package(models.Model):
    package_name = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    appointments_got = models.IntegerField(null=True)
    appointments_left = models.IntegerField(null=True)
    specialization = models.ForeignKey('administrator.Specializations', on_delete=models.CASCADE, related_name='package', null=True)
    doctor = models.ForeignKey('doctor.DoctorProfiles', on_delete=models.CASCADE, related_name='package', null=True)
    customer = models.ForeignKey('customer.CustomerProfile', on_delete=models.CASCADE, related_name='customer_package', null=True)
    is_couple = models.BooleanField(default=False)
    expires_on = models.DateField(null=True)


class Suggested_packages(models.Model):
    suggested_by = models.ForeignKey('doctor.DoctorProfiles', on_delete=models.CASCADE, related_name='suggested_packages')
    package = models.ForeignKey('doctor.DoctorPaymentRules', on_delete=models.CASCADE, related_name='suggested_packages')
    customer = models.ForeignKey('customer.CustomerProfile', on_delete=models.CASCADE, related_name='suggested_packages')



