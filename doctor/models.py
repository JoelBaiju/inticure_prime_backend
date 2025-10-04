from django.db import models
from django.contrib.auth.models import User
from administrator.models import *
# Create your models here.


# Calendar model removed - using direct date fields instead



class DoctorProfiles(models.Model):
    doctor_profile_id       = models.BigAutoField(primary_key=True)
    first_name              = models.CharField(max_length=50 , null=True)
    last_name               = models.CharField(max_length=50 , null=True)
    user                    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile',null=True)
    country                 = models.ForeignKey(Countries , on_delete=models.CASCADE ,related_name='doctor_profile' , null = True)
    time_zone               = models.CharField(max_length=50, null=True, blank=True)
    doctor_flag             = models.CharField(max_length=10,null=True)
    mobile_number           = models.CharField(max_length=12 ,null= True , unique=True)
    whatsapp_number        = models.CharField(max_length=15 ,null= True , blank=True)
    whatsapp_country_code   = models.CharField(max_length=5 ,null= True , blank=True)
    mobile_country_code     = models.CharField(max_length=5 ,null= True)
    email_id                = models.CharField(max_length=50 , null=True , unique=True)
    gender                  = models.CharField(max_length=10,null=True)
    qualification           = models.TextField(null=True)
    certificate_no          = models.TextField(null=True)
    certificate_file        = models.FileField(upload_to='certificates/', null=True, blank=True)
    address                 = models.TextField(null=True)   
    address_proof           = models.FileField(upload_to='address_proofs/', null=True, blank=True)

    sign_file_name          = models.FileField(upload_to='signatures/', null=True, blank=True)
    profile_pic             = models.FileField(upload_to='profile_pics/', null=True, blank=True)
    
    salutation              = models.CharField(max_length=10,null=True)
    doctor_bio              = models.CharField(null=True,max_length=10000)
    registration_year       = models.CharField(max_length=10,null=True)
    registration_number     = models.CharField(max_length=100,null=True)
    is_accepted             = models.BooleanField(default=False)
    rejected                = models.BooleanField(default=False)
    rejection_reason        = models.CharField(null=True, max_length=500)
    joined_date             = models.DateTimeField(auto_now_add=True,null= True)
    accepted_date           = models.DateField(null=True, blank=True)
    experience              = models.CharField(max_length=10 , null=True)
    dob                     = models.DateField(null=True)
    is_prescription_allowed        = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.first_name}  {self.last_name} -{self.gender} - {self.doctor_flag}"
    

class DoctorSpecializations(models.Model):
    specialization  = models.ForeignKey(Specializations , on_delete= models.CASCADE , related_name='doctor_specializations' , null=True)
    time_duration   = models.IntegerField(null=True)
    doctor          = models.ForeignKey(DoctorProfiles,on_delete= models.CASCADE ,null=True,related_name='doctor_specializations' )


class DoctorLanguages(models.Model):
    doctor      = models.ForeignKey(DoctorProfiles,on_delete= models.CASCADE ,null=True,related_name='known_languages' )
    language    = models.ForeignKey(LanguagesKnown , on_delete=models.CASCADE, max_length=100,null=True)













class Medications(models.Model):
    medication_id=models.BigAutoField(primary_key=True)
    prescription_id=models.BigIntegerField()
    medication=models.TextField()
    duration_number=models.TextField()
    duration=models.TextField()
    side_effects=models.TextField()
    consumption_detail=models.TextField()
    can_substitute=models.IntegerField()
class ConsumptionTime(models.Model):
    medication_id=models.BigIntegerField()
    prescription_id=models.BigIntegerField(null=True)
    consumption_time=models.CharField(max_length=20)
class AnalysisInfo(models.Model):
    appointment_id=models.BigIntegerField()
    doctor_id=models.BigIntegerField(null=True)
    uploaded_time=models.TimeField(auto_now=True)
    uploaded_date=models.DateField(auto_now=True)
    analysis_info_text=models.TextField(null=True)
    analysis_info_path=models.TextField(null=True)
    file_name=models.TextField(null=True)
    file_size=models.CharField(null=True,max_length=20)






class DoctorMapping(models.Model):
    appointment_id=models.BigIntegerField(null=True)
    mapped_doctor=models.IntegerField(null=True)
    doctor_flag=models.CharField(max_length=10,null=True)
    added_doctor=models.IntegerField(default=0)

class FollowUpReminder(models.Model):
    appointment_id=models.BigIntegerField(null=True)
    follow_up_for=models.CharField(max_length=100,null=True)
    remarks=models.TextField(null=True)
    duration=models.CharField(max_length=100,null=True)

class AppointmentDiscussion(models.Model):
    appointment_id=models.BigIntegerField(null=True)
    content=models.TextField(null=True)
    is_query=models.IntegerField(default=0)
    is_reply=models.IntegerField(default=0)
    created_date=models.DateField(auto_now=True)
    created_time=models.TimeField(auto_now=True)

class AppointmentCancellationLog(models.Model):
    appointment_id=models.BigIntegerField()
    cancelled_date=models.DateField(auto_now=True)
    cancelled_time=models.TimeField(auto_now=True)
    cancelled_by=models.CharField(max_length=20)

 












# ======================================================common for both junior and senior :-





class DoctorAvailableHours(models.Model):
    doctor      = models.ForeignKey(DoctorProfiles , on_delete=models.CASCADE , related_name='doctor_available_hours')
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    # date        = models.DateTimeField






class DoctorAppointment(models.Model):
    doctor = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE , null=True , related_name='doctor_appointment')
    specialization = models.ForeignKey("administrator.Specializations", on_delete=models.SET_NULL, null=True , related_name='doctor_appointment')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    appointment = models.ForeignKey('analysis.AppointmentHeader', on_delete=models.CASCADE, related_name='doctor_appointment', null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    
 



# =================================================================only for junior doctors :-




class DoctorPaymentRules(models.Model):
    pricing_name = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Optional name for this doctor's specific pricing rule"
    )

    doctor           = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='payment_assignments')
    specialization   = models.ForeignKey(Specializations, on_delete=models.CASCADE, related_name='doctor_assignments' ,blank=True, null=True)
    country          = models.ForeignKey(Countries, on_delete=models.CASCADE, related_name='doctor_assignments',blank=True , null= True)

    general_rule    = models.ForeignKey(
        GeneralPaymentRules,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_doctors',
        help_text="Optional. Link to reusable rule template"
    )

    session_count               = models.PositiveIntegerField(default=1, help_text="Number of sessions for this override")

    custom_doctor_fee_single    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_user_total_fee_single = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    custom_doctor_fee_couple     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_user_total_fee_couple = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    actual_price_single          = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_price_couple          = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('doctor', 'specialization', 'country', 'session_count')

    def __str__(self):
        label = self.pricing_name or f"{self.doctor} | {self.specialization} | {self.country} | {self.session_count} sessions"
        return f"[Doctor] {label}"

    def get_effective_payment(self, *args, **kwargs):
        def get_value(attr, fallback_attr):
            val = getattr(self, attr, None)
            if val is not None:
                return float(val)
            if self.general_rule:
                return float(getattr(self.general_rule, fallback_attr, 0) or 0)
            return 0.0

        return {
            "custom_doctor_fee_single": get_value("custom_doctor_fee_single", "doctor_fee_single"),
            "custom_user_total_fee_single": get_value("custom_user_total_fee_single", "user_total_fee_single"),
            "custom_doctor_fee_couple": get_value("custom_doctor_fee_couple", "doctor_fee_couple"),
            "custom_user_total_fee_couple": get_value("custom_user_total_fee_couple", "user_total_fee_couple"),
            "actual_price_single": get_value("actual_price_single", "actual_price_single"),
            "actual_price_couple": get_value("actual_price_couple", "actual_price_couple"),
            "session_count": int(get_value("session_count", "session_count")),
        }




class Payouts(models.Model):
    doctor = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=6 , null=True)
    currency_symbol = models.CharField(max_length=6 , null=True)
    initiated_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=20)



class Doctor_Bank_Account(models.Model):
    doctor              = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='bank_account')
    bank_name           = models.CharField(max_length=100)
    account_number      = models.CharField(max_length=100)
    ifsc_code           = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)









