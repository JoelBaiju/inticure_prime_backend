from django.db import models

# # Create your models here.
# from django.db import models
# from django.contrib.auth.models import User

# # Administrator Models
class AnalysisAnswerType(models.Model):
    answer_type = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'analysis_answertype'



# class AnalysisAppointmentQuestions(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     question = models.ForeignKey('AnalysisQuestionnaire', on_delete=models.CASCADE)
#     question_text = models.TextField()

#     class Meta:
#         db_table = 'analysis_appointmentquestions'


class AnalysisAppointmentAnswers(models.Model):
    appointment_question = models.ForeignKey('AnalysisAppointmentQuestions', on_delete=models.CASCADE)
    option = models.ForeignKey('AnalysisOptions', on_delete=models.SET_NULL, null=True)
    answer = models.TextField(null=True)

    class Meta:
        db_table = 'analysis_appointmentanswers'

# class AnalysisAppointmentHeader(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     category = models.ForeignKey('AnalysisCategory', on_delete=models.CASCADE)
#     appointment_status = models.IntegerField()
#     booked_on = models.DateField()
#     is_free = models.IntegerField()
#     appointment_date = models.DateField()
#     appointment_time = models.TimeField(null=True)
#     type_booking = models.CharField(max_length=20)
#     followup = models.ForeignKey('DoctorFollowupReminder', on_delete=models.SET_NULL, null=True)
#     senior_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True, related_name='senior_appointments')
#     junior_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True, related_name='junior_appointments')
#     appointment_time_slot_id = models.CharField(max_length=40, null=True)
#     escalated_date = models.DateField(null=True)
#     escalated_time_slot = models.CharField(max_length=20, null=True)
#     followup_remark = models.TextField(null=True)
#     gender_pref = models.CharField(max_length=20, null=True)
#     language_pref = models.CharField(max_length=20, null=True)
#     booked_on_time = models.TimeField(null=True)
#     meeting_link = models.CharField(max_length=200, null=True)
#     senior_meeting_link = models.CharField(max_length=200, null=True)
#     followup_created_by = models.CharField(max_length=20, null=True)
#     followup_created_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     customer_message = models.TextField(null=True)
#     payment_done = models.IntegerField(null=True)
#     payment_required = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'analysis_appointmentheader'


# class AnalysisCategory(models.Model):
#     title = models.CharField(max_length=100)
#     description = models.CharField(max_length=250, null=True)
#     image = models.CharField(max_length=100, null=True)

#     class Meta:
#         db_table = 'analysis_category'

# class AnalysisEmailOtpVerify(models.Model):
#     email = models.CharField(max_length=100)
#     otp = models.CharField(max_length=10, null=True)

#     class Meta:
#         db_table = 'analysis_emailotpverify'

# class AnalysisInvoices(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     bill_for = models.CharField(max_length=25)
#     issue_date = models.DateField()
#     due_date = models.DateField()
#     total = models.IntegerField()
#     status = models.IntegerField()
#     address = models.CharField(max_length=50, null=True)
#     age = models.IntegerField(null=True)
#     appointment_date = models.DateField(null=True)
#     appointment_time = models.TextField(null=True)
#     discounts = models.IntegerField(null=True)
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     doctor_name = models.CharField(max_length=100, null=True)
#     email = models.CharField(max_length=30, null=True)
#     issue_time = models.TimeField(null=True)
#     mode_of_pay = models.CharField(max_length=20, null=True)
#     service = models.CharField(max_length=60, null=True)
#     tax = models.IntegerField(null=True)
#     vendor_fee = models.IntegerField(null=True)
#     date_of_birth = models.DateField(null=True)
#     mobile_number = models.BigIntegerField(null=True)
#     appointment_for = models.CharField(max_length=20, null=True)
#     gender = models.CharField(max_length=15, null=True)
#     category = models.ForeignKey(AnalysisCategory, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'analysis_invoices'

# class AnalysisOptions(models.Model):
#     question = models.ForeignKey('AnalysisQuestionnaire', on_delete=models.CASCADE)
#     option = models.CharField(max_length=100)

#     class Meta:
#         db_table = 'analysis_options'

# class AnalysisOtpVerify(models.Model):
#     mobile_number = models.BigIntegerField()
#     otp = models.CharField(max_length=10, null=True)

#     class Meta:
#         db_table = 'analysis_otpverify'

# class AnalysisQuestionnaire(models.Model):
#     question = models.CharField(max_length=300)
#     answer_type = models.CharField(max_length=50)
#     category = models.ForeignKey(AnalysisCategory, on_delete=models.CASCADE)
#     customer_gender = models.CharField(max_length=30, null=True)

#     class Meta:
#         db_table = 'analysis_questionnaire'
