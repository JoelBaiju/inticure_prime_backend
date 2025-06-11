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
    
    
    
import json
from django.db import models

class UserPreferredDoctors(models.Model):
    user_id = models.BigIntegerField()
    doctor_ids = models.CharField(max_length=500, default='[]')  # Stored as JSON list

    def get_doctor_ids(self):
        """Returns doctor IDs as a list"""
        try:
            return json.loads(self.doctor_ids)
        except json.JSONDecodeError:
            return []

    def add_doctor(self, doctor_id):
        ids = self.get_doctor_ids()
        if doctor_id not in ids:
            ids.append(doctor_id)
            self.doctor_ids = json.dumps(ids)

    def remove_doctor(self, doctor_id):
        ids = self.get_doctor_ids()
        if doctor_id in ids:
            ids.remove(doctor_id)
            self.doctor_ids = json.dumps(ids)

    def clear_doctors(self):
        """Removes all doctor IDs"""
        self.doctor_ids = json.dumps([])


    def __str__(self):
        return f"User {self.user_id} Preferences"
