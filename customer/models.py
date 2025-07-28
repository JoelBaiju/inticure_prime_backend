from django.db import models
from django.contrib.auth.models import User
from administrator.models import Countries

# Create your models here.
class CustomerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_profile')
    age=models.IntegerField(blank=True, null=True)
    gender=models.CharField(max_length=20,blank=True, null=True)
    other_gender=models.CharField(max_length=20,blank=True, null=True)
    address=models.CharField(max_length=50,blank=True, null=True)
    date_of_birth=models.DateField(blank=True, null=True,auto_now_add=False)
    mobile_number=models.BigIntegerField(blank=True, null=True)
    country_details = models.ForeignKey(Countries, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    profile_pic=models.TextField(null=True)
    completed_first_analysis = models.BooleanField(default=False)
    preferred_name = models.CharField(max_length=110,blank=True, null=True)
    weight = models.CharField(max_length=255, null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} -{self.user.first_name}-{self.user.last_name}- {self.preferred_name if self.preferred_name else 'No Preferred Name'}"

class Extra_questions(models.Model):
    question = models.CharField(max_length=255, null=True, blank=True)

class Extra_questions_answers(models.Model):
    question = models.ForeignKey(Extra_questions, on_delete=models.CASCADE, related_name='extra_questions_answers')
    answer = models.CharField(max_length=255, null=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='extra_questions_answers')

class AppointmentRatings(models.Model):
    appointment_id=models.BigIntegerField(null=True)
    doctor_id=models.BigIntegerField(null=True)
    user_id=models.BigIntegerField(null=True)
    rating_comments=models.TextField(null=True)
    rating=models.IntegerField(null=True)
    app_rating=models.IntegerField(null=True)
    added_by=models.CharField(max_length=25)

class StripeCustomer(models.Model):
    stripe_customer_id = models.BigAutoField(primary_key=True)
    stripe_customer_token_id = models.TextField()
    customer_id = models.IntegerField()


class Refund(models.Model):
    refund_id=models.CharField(max_length=50)
    customer_id=models.IntegerField()
    refund_status=models.IntegerField(default=0)
    refund_requested_date=models.DateField()
    refund_processed_date=models.DateField(null=True)
    appointment_id=models.IntegerField()
    appointment_date=models.DateField()
    refund_amount=models.IntegerField(default=0)
    
