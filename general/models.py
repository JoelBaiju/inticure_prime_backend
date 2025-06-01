from django.db import models

# Create your models here.




class Phone_OTPs(models.Model):
    otp             = models.CharField(max_length=20)
    phone           = models.CharField(max_length=11 )
    country_code    = models.CharField(max_length=5, default='+91')  
    exists          = models.BooleanField(default=False)
    
class Email_OTPs(models.Model):
    otp             = models.CharField(max_length=20)
    email           = models.CharField(max_length=100 )
    exists          = models.BooleanField(default=False)    
    