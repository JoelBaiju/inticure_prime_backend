from contextlib import nullcontext
from email.policy import default
from enum import auto, unique
from faulthandler import is_enabled
from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from customer.models import CustomerProfile
# Create your models here.
"""Holds the catergory of medical issues"""


class Category(models.Model):
    title       = models.CharField(max_length=100)
    description = models.CharField(max_length=250, null=True ,blank=True)

    
    def __str__(self):
        return self.title +str(self.id)
    
    
"""Answer type selection"""
class AnswerType(models.Model):
    answer_type=models.CharField(max_length=100,null=True)



"""Holds the details  of analysis questions  that user submit before taking an appointment"""


class Questionnaire(models.Model):
    question        = models.CharField(max_length=300)
    answer_type     = models.CharField(max_length=50)
    category        = models.ForeignKey(Category , on_delete=models.CASCADE, related_name='questionnaire',null=True, blank=True)
    customer_gender = models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.question
    
    
"""Holds the details  of options of  questions  that user submit before taking an appointment"""


class Options(models.Model):
    question    = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='options',null=True , blank=True)
    option      = models.CharField(max_length=100)

    
    def __str__(self):
        return self.option
    
    

"""Holds the details  of an appointment.here appointment_status 1= , 2= , 3= cancel, 4 = ,5 = , 6= completed, 7 =reschedule ,8= ,9= order marked no show"""
from doctor.models import DoctorProfiles

class AppointmentHeader(models.Model):
    appointment_id              = models.BigAutoField(primary_key=True)
    customer                    = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='appointment_header',null=True, blank=True)
    is_couple                   = models.BooleanField(default=False)
    partner_customer            = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='partner_appointment_header', null=True, blank=True)
    category                    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='appointment_header',null=True, blank=True)
    appointment_status          = models.CharField(max_length=50 , null=True , blank=True)
    status_detail               = models.CharField(max_length=5000 , null=True , blank=True)
    start_time                  = models.DateTimeField(null=True)
    end_time                    = models.DateTimeField(null=True)

    doctor                      = models.ForeignKey(DoctorProfiles, on_delete = models.CASCADE , null=True ,related_name='appointment_header')
    
    followup                    = models.BooleanField(default=False)
    followup_of_appointment     = models.ForeignKey('self',null=True,on_delete=models.SET_NULL , related_name="follow_appointment")
    followup_remark             = models.TextField(null=True)

    booked_on                   = models.DateTimeField(auto_now=True)
   
    language_pref               = models.CharField(max_length=20,null=True)
    gender_pref                 = models.CharField(max_length=20,null=True)
    meeting_link                = models.CharField(max_length=200,null=True)

    customer_message            = models.TextField(null=True)
    payment_required            = models.BooleanField(default=True)
    payment_done                = models.BooleanField(default=False)
    analysis_session            = models.OneToOneField("AnalysisSession", null=True, blank=True, on_delete=models.SET_NULL)
    file_is_open                = models.BooleanField(default=True)
    is_referred                 = models.BooleanField(default=False)
    referral                    = models.ForeignKey('Referral', on_delete=models.CASCADE, related_name='appointment_header', null=True, blank=True)
    specialization              = models.ForeignKey('administrator.Specializations', on_delete=models.SET_NULL, related_name='appointment_header', null=True, blank=True)
    completed                   = models.BooleanField(default=False )
    reason                      = models.CharField(max_length=200, null=True , blank=True)
    booked_by                   = models.CharField(max_length=200, null=True , blank=True)
    package_included            = models.BooleanField(default=False)
    payment_rule                = models.ForeignKey('doctor.DoctorPaymentRules', on_delete=models.SET_NULL, related_name='appointment_header', null=True, blank=True)
    package                     = models.ForeignKey('customer.Customer_Package', on_delete=models.SET_NULL, related_name='appointment_header', null=True, blank=True)                                                                                                                    
    package_used                = models.BooleanField(default=False)
    confirmed_by_admin          = models.BooleanField(default=False)




class Appointment_customers(models.Model):
    appointment     = models.ForeignKey(AppointmentHeader, on_delete=models.CASCADE, related_name='appointment_customers')
    customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='appointment_customers')
    class Meta:
        unique_together = ('appointment', 'customer')

"""Holds the details  of analysis questions user submitted before taking appointment"""




class Observation_Notes(models.Model):
    note        = models.TextField(null=True)
    appointment = models.ForeignKey(AppointmentHeader , on_delete=models.CASCADE , related_name='observation_notes' , null=True)
    date        = models.DateTimeField(auto_now=True)
    customer    = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='observation_notes', null=True, blank=True)

class Follow_Up_Notes(models.Model):
    note        = models.TextField(null=True)
    appointment = models.ForeignKey(AppointmentHeader , on_delete=models.CASCADE , related_name='follow_up_notes' , null=True)
    date        = models.DateTimeField(auto_now=True)
    customer    = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='follow_up_notes', null=True, blank=True)
 

class Referral(models.Model):
    # customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='referrals', null=True, blank=True)
    doctor          = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='referrals_made', null=True, blank=True)
    referred_doctor = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='referrals', null=True, blank=True)
    referred_date   = models.DateTimeField(auto_now_add=True)
    referral_notes  = models.TextField(null=True, blank=True)
    specialization  = models.ForeignKey('administrator.Specializations', on_delete=models.CASCADE , related_name='referrals', null=True)
    is_couple       = models.BooleanField(default=False)
    converted_to_appointment = models.BooleanField(default=False)

class Referral_customer(models.Model):
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='referral_customers', null=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='referral_customers', null=True, blank=True)
    class Meta:
        unique_together = ('referral', 'customer')



class Prescribed_Medications(models.Model):
    customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='prescribed_medications', null=True, blank=True)
    doctor          = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='prescribed_medications', null=True, blank=True)
    appointment     = models.ForeignKey(AppointmentHeader, on_delete=models.CASCADE, related_name='prescribed_medications', null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    instruction     = models.TextField(null=True, blank=True)
    duration        = models.CharField(max_length=50 , null=True)
    frequency       = models.CharField (max_length=100 , null=True)
    dosage          = models.CharField(max_length=100)
    strength        = models.CharField(max_length=100)
    medicine_name   = models.CharField(max_length=200)
    is_active       = models.BooleanField(default=True)
    validity        = models.DateField(null=True)



class Prescribed_Tests(models.Model):
    customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='prescribed_tests', null=True, blank=True)
    doctor          = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='prescribed_tests', null=True, blank=True)
    appointment     = models.ForeignKey(AppointmentHeader, on_delete=models.CASCADE, related_name='prescribed_tests', null=True, blank=True)
    test_name       = models.CharField(max_length=100)
    instruction     = models.TextField( null=True , blank=True)
    created_at      = models.DateTimeField(auto_now_add=True , null=True)
    updated_at      = models.DateTimeField(auto_now=True ,null=True)
    submitted       = models.BooleanField(default=False)

class Notes_for_patient(models.Model):
    customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='notes_for_patient', null=True, blank=True)
    doctor          = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='notes_for_patient', null=True, blank=True)
    appointment     = models.ForeignKey(AppointmentHeader, on_delete=models.CASCADE, related_name='notes_for_patient', null=True, blank=True)
    note            = models.TextField( null=True , blank=True)
    created_at      = models.DateTimeField(auto_now_add=True , null=True)
    updated_at      = models.DateTimeField(auto_now=True ,null=True)


class Prescrption_validity(models.Model):
    valid_till  = models.DateField(null=True)
    active      = models.BooleanField(default=True)
    doctor      = models.ForeignKey(DoctorProfiles, on_delete=models.CASCADE, related_name='prescription_validity', null=True, blank=True)
    customer    = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='prescription_validity', null=True, blank=True)
    last_updated= models.DateTimeField(auto_now=True)
    

class Doctor_Suggested_Plans(models.Model):
    refferral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='suggested_plans', null=True, blank=True)
    plan      = models.ForeignKey('doctor.DoctorPaymentRules' , on_delete=models.CASCADE, related_name='suggested_plans', null=True, blank=True)


class Reschedule_history(models.Model):
    initiated_by        = models.CharField(max_length=50)
    appointment         = models.ForeignKey(AppointmentHeader , on_delete=models.CASCADE , related_name='reschedule_history')
    reason              = models.CharField(max_length=200 , null=True , blank=True)
    initiated_on        = models.DateTimeField(auto_now=True)
    previous_start_time = models.DateTimeField(null=True)
    previous_end_time   = models.DateTimeField(null=True)
    new_start_time      = models.DateTimeField(null=True)
    new_end_time        = models.DateTimeField(null=True)  



class Cancel_history(models.Model):
    appointment  = models.ForeignKey(AppointmentHeader , on_delete=models.CASCADE , related_name='cancel_history')
    reason       = models.CharField(max_length=200 , null=True , blank=True)
    initiated_on = models.DateTimeField(auto_now=True)




# analysis/models.py
import uuid
from django.db import models
from analysis.models import Category

from django.db.models import Q, F, CheckConstraint

class Meeting_Tracker(models.Model):
    meeting_link                    = models.CharField(max_length=200, null=True)
    meeting_code                    = models.CharField(max_length=29, null=True)
    appointment                     = models.ForeignKey(AppointmentHeader, on_delete=models.CASCADE, related_name='meeting_tracker', null=True)
    created_at                      = models.DateTimeField(auto_now=True, null=True)
    is_enabled                      = models.BooleanField(default=False, null=True)
    doctor_meeting_id               = models.CharField(max_length=50, null=True)
    customer_1                      = models.ForeignKey('customer.CustomerProfile', on_delete=models.CASCADE, null=True, related_name='meeting_tracker_customer_1')
    customer_2                      = models.ForeignKey('customer.CustomerProfile', on_delete=models.CASCADE, null=True, related_name='meeting_tracker_customer_2')
    customer_1_meeting_id           = models.CharField( null=True , max_length=50)
    customer_2_meeting_id           = models.CharField( null=True , max_length=50)
    doctor_joined                   = models.BooleanField(default=False, null=True)
    customer_1_joined               = models.BooleanField(default=False, null=True)
    customer_2_joined               = models.BooleanField(default=False, null=True)
    customer_1_attendence_confirmed = models.BooleanField(default=False, null=True)
    customer_2_attendence_confirmed = models.BooleanField(default=False, null=True)
    doctor_attendence_confirmed     = models.BooleanField(default=False, null=True)
    doctor_meeting_link             = models.CharField(max_length=200, null=True)
    customer_1_meeting_link         = models.CharField(max_length=200, null=True)
    customer_2_meeting_link         = models.CharField(max_length=200, null=True)   
    reminder_task_id                = models.CharField(max_length = 50, null=True)
    monitor_task_id                = models.CharField(max_length = 50, null=True)
    class Meta:
        constraints = [
            CheckConstraint(
                check=~Q(doctor_meeting_id=F('customer_1_meeting_id')) & ~Q(doctor_meeting_id=F('customer_2_meeting_id')),
                name='doctor_and_customer_id_different'
            )
        ]

    def save(self, *args, **kwargs):
        """Extra safeguard in Python to ensure IDs differ."""
        if self.doctor_meeting_id == self.customer_1_meeting_id or self.doctor_meeting_id == self.customer_2_meeting_id:
            raise ValueError("Doctor and customer meeting IDs must be different.")
        super().save(*args, **kwargs)






class AnalysisSession(models.Model):
    token                       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    gender                      = models.CharField(max_length=10, null=True, blank=True)
    category                    = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    phone_number                = models.CharField(max_length=20, null=True, blank=True)
    email                       = models.EmailField(null=True, blank=True)
    otp                         = models.CharField(max_length=10, null=True, blank=True)
    otp_verified                = models.BooleanField(default=False)
    created_at                  = models.DateTimeField(auto_now_add=True)
    gender_preference           = models.CharField(max_length=50, null=True, blank=True)
    language_preference         = models.CharField(max_length=50, null=True, blank=True)
    preferred_date              = models.DateField(null=True, blank=True)
    specialization              = models.ForeignKey('administrator.Specializations', on_delete=models.SET_NULL, null=True, blank=True, related_name='analysis_sessions')
    country                     = models.CharField(max_length=100, null=True, blank=True)
    is_couple                   = models.BooleanField(default=False)
    is_junior                   = models.BooleanField(default=False)
    alignment_minutes           = models.IntegerField(null=True, blank=True)
    session_status              = models.CharField(max_length=20, default='started')
    customer                    = models.ForeignKey('customer.CustomerProfile' , on_delete=models.CASCADE , null=True , related_name='analysis_session')
    time_zone                   = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return str(self.token)



class AppointmentQuestionsAndAnswers(models.Model):
    customer        = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE,related_name='appointment_questions_and_answers',null=True, blank=True)
    question        = models.ForeignKey(Questionnaire, on_delete=models.CASCADE,related_name='appointment_questions',null=True, blank=True)
    answer          = models.ForeignKey(Options, on_delete=models.CASCADE,related_name='appointment_answers',null=True, blank=True)
    tempsession     = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE,related_name='temp_questionnaire_answers',null=True, blank=True)

