from django.db import models

# Create your models here
class Phone_OTPs(models.Model):
    otp             = models.CharField(max_length=20)
    phone           = models.CharField(max_length=11)
    country_code    = models.CharField(max_length=5, default='+91')
    exists          = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True , null=True)  # NEW

    def __str__(self):
        return f"{self.country_code}{self.phone} - {self.otp}"


class Email_OTPs(models.Model):
    otp             = models.CharField(max_length=20)
    email           = models.CharField(max_length=100)
    exists          = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True , null=True)  # NEW

    def __str__(self):
        return f"{self.email} - {self.otp}"

    
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



from customer.models import CustomerProfile



class PreTransactionData(models.Model):
    pretransaction_id=models.BigAutoField(primary_key=True)
    customer=models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='temporary_transaction_data', null=True, blank=True)
    currency=models.CharField(max_length=10,null=True)
    total_amount=models.IntegerField(null=True)
    appointment=models.ForeignKey("analysis.AppointmentHeader",on_delete=models.CASCADE, related_name='temporary_transaction_data', null=True, blank=True)
    discount=models.IntegerField(null=True)
    coupon_id=models.IntegerField(null=True)
    tax=models.IntegerField(null=True)
    vendor_fee=models.IntegerField(null=True)
    gateway=models.CharField(max_length=20, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_payment_link = models.CharField(max_length=300, null=True)



class Invoices(models.Model):
    invoice_id=models.BigAutoField(primary_key=True)
    appointment_id=models.IntegerField()
    user_id=models.IntegerField()
    bill_for=models.CharField(max_length=25)
    gender=models.CharField(max_length=15,null=True)
    age=models.IntegerField(null=True)
    mobile_number=models.BigIntegerField(null=True)
    date_of_birth=models.DateField(null=True)
    address=models.CharField(max_length=50,null=True)
    email=models.CharField(max_length=30,null=True)
    appointment_date=models.DateField(null=True)
    appointment_time=models.TextField(null=True)
    appointment_for=models.CharField(max_length=20,null=True)
    issue_date=models.DateField(auto_now=True)
    issue_time=models.TimeField(auto_now=True,null=True)
    service=models.CharField(max_length=60,null=True)
    due_date=models.DateField()
    vendor_fee=models.IntegerField(null=True)
    tax=models.IntegerField(null=True)
    discounts=models.IntegerField(null=True)
    total=models.IntegerField()
    status=models.IntegerField() 
    mode_of_pay=models.CharField(max_length=20,null=True)
    doctor_id=models.IntegerField(null=True)
    doctor_name=models.CharField(max_length=100,null=True)
    category_id=models.IntegerField(null=True)