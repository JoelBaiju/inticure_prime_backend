from django.db import models
from customer.models import CustomerProfile
from django.contrib.auth.models import User


class Phone_OTPs(models.Model):
    otp             = models.CharField(max_length=20)
    phone           = models.CharField(max_length=17)
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



class PreTransactionData(models.Model):
    pretransaction_id   =   models.BigAutoField(primary_key=True)
    customer            =   models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='temporary_transaction_data', null=True, blank=True)
    currency            =   models.CharField(max_length=10,null=True)
    total_amount        =   models.IntegerField(null=True)
    appointment         =   models.ForeignKey("analysis.AppointmentHeader",on_delete=models.CASCADE, related_name='temporary_transaction_data', null=True, blank=True)
    discount            =   models.IntegerField(null=True)
    coupon_id           =   models.IntegerField(null=True)
    tax                 =   models.IntegerField(null=True)
    vendor_fee          =   models.IntegerField(null=True)
    gateway             =   models.CharField(max_length=20, null=True, blank=True)
    razorpay_order_id   =   models.CharField(max_length=100, null=True, blank=True)
    stripe_payment_link =   models.CharField(max_length=300, null=True)
    



class StripeTransactions(models.Model):
    pretransaction      = models.ForeignKey(PreTransactionData, on_delete=models.CASCADE, related_name='stripe_transactions', null=True)
    created_at          = models.DateTimeField(auto_now_add=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"Stripe Transaction {self.id} for PreTransaction {self.pretransaction.pretransaction_id if self.pretransaction else 'N/A'}"


class RazorpayTransaction(models.Model):
    pretransaction      = models.ForeignKey(PreTransactionData, on_delete=models.CASCADE, related_name='razorpay_transactions', null=True)
    created_at          = models.DateTimeField(auto_now_add=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Razorpay Transaction {self.id} for PreTransaction {self.pretransaction.pretransaction_id if self.pretransaction else 'N/A'}"




class Transactions(models.Model):
    pretransaction_data = models.ForeignKey(PreTransactionData , on_delete=models.CASCADE, related_name='transactions', null=True)
    invoice_id=models.IntegerField(null=True)
    transaction_amount=models.IntegerField(null=True)
    transaction_date=models.DateTimeField(auto_now=True)
    payment_status=models.CharField(default="pending", max_length=20)




class Invoices(models.Model):
    invoice_id          =   models.BigAutoField(primary_key=True)
    appointment_id      =   models.IntegerField()
    user_id             =   models.IntegerField()
    bill_for            =   models.CharField(max_length=25)
    gender              =   models.CharField(max_length=15,null=True)
    age                 =   models.IntegerField(null=True)
    mobile_number       =   models.BigIntegerField(null=True)
    date_of_birth       =   models.DateField(null=True)
    address             =   models.CharField(max_length=50,null=True)
    email               =   models.CharField(max_length=30,null=True)
    appointment_date    =   models.DateField(null=True)
    appointment_time    =   models.TextField(null=True)
    appointment_for     =   models.CharField(max_length=20,null=True)
    issue_date          =   models.DateField(auto_now=True)
    issue_time          =   models.TimeField(auto_now=True,null=True)
    service             =   models.CharField(max_length=60,null=True)
    due_date            =   models.DateField()
    vendor_fee          =   models.IntegerField(null=True)
    tax                 =   models.IntegerField(null=True)
    discounts           =   models.IntegerField(null=True)
    total               =   models.IntegerField()
    status              =   models.IntegerField() 
    mode_of_pay         =   models.CharField(max_length=20,null=True)
    doctor_id           =   models.IntegerField(null=True)
    doctor_name         =   models.CharField(max_length=100,null=True)
    category_id         =   models.IntegerField(null=True)






class Reminder_Sent_History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_sent_history')
    user_is_customer = models.BooleanField(default=False)
    appointment = models.ForeignKey("analysis.AppointmentHeader", on_delete=models.CASCADE, related_name='reminder_sent_history')
    whatsapp_number = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    body = models.CharField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)

    
    message_id = models.CharField(max_length=100)
    provider_response = models.TextField(null=True)
    status = models.CharField(max_length=50)





class CommonFileUploader(models.Model):
    customer=models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='common_files', null=True)
    appointment=models.ForeignKey('analysis.AppointmentHeader', on_delete=models.CASCADE, related_name='common_files', null=True)
    uploaded_on = models.DateTimeField(auto_now_add=True , null=True)
    common_file=models.FileField(null=True,upload_to='tests&common_files/')
    file_name=models.CharField(max_length=100,null=True)
    uploaded_by_doctor = models.BooleanField(default=False)

