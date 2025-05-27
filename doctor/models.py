# from django.db import models
# from analysis.models import *

# # Create your models here.

# # Doctor Models




# class DoctorDoctorProfiles(models.Model):
#     location = models.CharField(max_length=30)
#     department = models.CharField(max_length=20)
#     doctor_flag = models.CharField(max_length=10)
#     mobile_number = models.CharField(max_length=12)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     specialization = models.CharField(max_length=20)
#     gender = models.CharField(max_length=10, null=True)
#     time_slot_from = models.IntegerField(null=True)
#     time_slot_to = models.IntegerField(null=True)
#     working_date_frm = models.DateField(null=True)
#     working_date_to = models.DateField(null=True)
#     signature = models.TextField(null=True)
#     address = models.TextField(null=True)
#     is_accepted = models.IntegerField(null=True)
#     qualification = models.TextField(null=True)
#     address_proof = models.TextField(null=True)
#     registration_certificate = models.TextField(null=True)
#     profile_pic = models.TextField(null=True)
#     certificate_no = models.TextField(null=True)
#     addr_file_name = models.TextField(null=True)
#     addr_file_size = models.CharField(max_length=20, null=True)
#     reg_file_name = models.TextField(null=True)
#     reg_file_size = models.CharField(max_length=20, null=True)
#     sign_file_name = models.TextField(null=True)
#     sign_file_size = models.CharField(max_length=20, null=True)
#     profile_file_name = models.TextField(null=True)
#     profile_file_size = models.TextField(null=True)
#     doctor_bio = models.CharField(max_length=10000, null=True)
#     registration_year = models.TextField(null=True)

#     class Meta:
#         db_table = 'doctor_doctorprofiles'



# class DoctorAnalysisInfo(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     uploaded_time = models.TimeField()
#     uploaded_date = models.DateField()
#     analysis_info_text = models.TextField(null=True)
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     analysis_info_path = models.TextField(null=True)
#     file_name = models.TextField(null=True)
#     file_size = models.CharField(max_length=20, null=True)

#     class Meta:
#         db_table = 'doctor_analysisinfo'

# class DoctorAppointmentCancellationLog(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     cancelled_date = models.DateField()
#     cancelled_time = models.TimeField()
#     cancelled_by = models.CharField(max_length=20)

#     class Meta:
#         db_table = 'doctor_appointmentcancellationlog'

# class DoctorAppointmentDiscussion(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)
#     content = models.TextField(null=True)
#     is_query = models.IntegerField()
#     is_reply = models.IntegerField()
#     created_date = models.DateField()
#     created_time = models.TimeField()

#     class Meta:
#         db_table = 'doctor_appointmentdiscussion'

# class DoctorAppointmentReschedule(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     reschedule_count = models.IntegerField()
#     rescheduled_time = models.TimeField(null=True)
#     rescheduled_date = models.DateField(null=True)
#     time_slot = models.CharField(max_length=30, null=True)
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     sr_rescheduled_date = models.DateField(null=True)
#     sr_rescheduled_time = models.CharField(max_length=30, null=True)

#     class Meta:
#         db_table = 'doctor_appointmentreshedule'

# class DoctorAppointmentTransferHistory(models.Model):
#     new_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True, related_name='new_transfers')
#     old_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True, related_name='old_transfers')
#     transfered_time = models.TimeField()
#     transfered_date = models.DateField()
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'doctor_appointmenttransferhistory'

# class DoctorCommonFileUploader(models.Model):
#     uploaded_time = models.TimeField(null=True)
#     common_file = models.CharField(max_length=100)
#     uploaded_date = models.DateField(null=True)

#     class Meta:
#         db_table = 'doctor_commonfileuploader'

# class DoctorConsumptionTime(models.Model):
#     medication = models.ForeignKey('DoctorMedications', on_delete=models.CASCADE)
#     consumption_time = models.CharField(max_length=20)
#     prescription = models.ForeignKey('DoctorPrescriptions', on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'doctor_consumptiontime'

# class DoctorDoctorAddedTimeSlots(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.CASCADE)
#     slot = models.IntegerField()
#     date = models.DateField(null=True)

#     class Meta:
#         db_table = 'doctor_doctoraddedtimeslots'

# class DoctorDoctorAvailableDates(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     date = models.DateField(null=True)
#     day = models.CharField(max_length=30, null=True)

#     class Meta:
#         db_table = 'doctor_doctoravailabledates'

# class DoctorDoctorAvailableTimeSlots(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     day = models.CharField(max_length=30, null=True)
#     time_slot_from = models.IntegerField(null=True)
#     time_slot_to = models.IntegerField(null=True)
#     slot_counter = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'doctor_doctoravailabletimeslots'

# class DoctorDoctorCalenderUpdate(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     date = models.DateField(null=True)
#     day = models.CharField(max_length=30, null=True)
#     time_slot_from = models.IntegerField(null=True)
#     time_slot_to = models.IntegerField(null=True)

#     class Meta:
#         db_table = 'doctor_doctorcalenderupdate'

# class DoctorDoctorLanguages(models.Model):
#     doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True)
#     languages = models.CharField(max_length=100, null=True)

#     class Meta:
#         db_table = 'doctor_doctorlanguages'

# class DoctorDoctorMapping(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)
#     mapped_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.SET_NULL, null=True, related_name='mapped_doctor')
#     doctor_flag = models.CharField(max_length=10, null=True)
#     added_doctor = models.ForeignKey('DoctorDoctorProfiles', on_delete=models.CASCADE, related_name='added_doctor')

#     class Meta:
#         db_table = 'doctor_doctormapping'

# class DoctorDoctorSpecializations(models.Model):
#     specialization = models.CharField(max_length=100)
#     time_duration = models.IntegerField(null=True)
#     description = models.TextField(null=True)

#     class Meta:
#         db_table = 'doctor_doctorspecializations'

# class DoctorEscalatedAppointment(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     appointment_status = models.IntegerField()
#     appointment_date = models.DateField()
#     time_slot = models.CharField(max_length=200)
#     specialization = models.CharField(max_length=200)
#     doctor = models.ForeignKey(DoctorDoctorProfiles, on_delete=models.CASCADE)
#     status = models.BooleanField()
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'doctor_escalatedappointment'

# class DoctorFollowupReminder(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)
#     follow_up_for = models.CharField(max_length=100, null=True)
#     remarks = models.TextField(null=True)
#     duration = models.CharField(max_length=100, null=True)

#     class Meta:
#         db_table = 'doctor_followupreminder'

# class DoctorJrDoctorEngagement(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     time_slot = models.CharField(max_length=30)

#     class Meta:
#         db_table = 'doctor_jrdoctorengagement'

# class DoctorJuniorDoctorSlots(models.Model):
#     doctor = models.ForeignKey(DoctorDoctorProfiles, on_delete=models.CASCADE)
#     date = models.DateField()
#     time_slot = models.CharField(max_length=200)
#     is_active = models.IntegerField()

#     class Meta:
#         db_table = 'doctor_juniordoctorslots'

# class DoctorMedications(models.Model):
#     prescription = models.ForeignKey('DoctorPrescriptions', on_delete=models.CASCADE)
#     medication = models.TextField()
#     duration = models.TextField()
#     side_effects = models.TextField()
#     consumption_detail = models.TextField()
#     duration_number = models.CharField(max_length=255)
#     can_substitute = models.IntegerField()

#     class Meta:
#         db_table = 'doctor_medications'

# class DoctorObeservations(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     observe = models.TextField()
#     uploaded_date = models.DateField()
#     uploaded_time = models.TimeField()
#     doctor = models.ForeignKey(DoctorDoctorProfiles, on_delete=models.SET_NULL, null=True)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'doctor_obeservations'

# class DoctorPatientMedicalHistory(models.Model):
#     doctor = models.ForeignKey(DoctorDoctorProfiles, on_delete=models.CASCADE)
#     doctor_flag = models.IntegerField()
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     height = models.CharField(max_length=20)
#     weight = models.CharField(max_length=20)
#     is_allergic = models.CharField(max_length=200)
#     medical_history = models.CharField(max_length=200)
#     prescription_history = models.CharField(max_length=200)
#     other_suppliments_history = models.CharField(max_length=200)
#     height_unit = models.CharField(max_length=20)
#     weight_unit = models.CharField(max_length=20)

#     class Meta:
#         db_table = 'doctor_patientmedicalhistory'

# class DoctorPrescriptions(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     uploaded_time = models.TimeField(null=True)
#     prescription = models.TextField(null=True)
#     uploaded_date = models.DateField(null=True)
#     prescript_file_name = models.TextField(null=True)
#     prescript_file_size = models.CharField(max_length=20, null=True)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'doctor_prescriptions'

# class DoctorPrescriptionsDetail(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     uploaded_time = models.TimeField()
#     uploaded_date = models.DateField()
#     prescriptions_text = models.TextField(null=True)
#     doctor = models.ForeignKey(DoctorDoctorProfiles, on_delete=models.SET_NULL, null=True)
#     tests_to_be_done = models.TextField(null=True)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         db_table = 'doctor_prescriptionsdetail'

# class DoctorRescheduleHistory(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     rescheduled_time = models.TimeField(null=True)
#     rescheduled_date = models.DateField(null=True)
#     time_slot = models.CharField(max_length=30, null=True)
#     doctor = models.CharField(max_length=100, null=True)
#     sr_rescheduled_date = models.DateField(null=True)
#     sr_rescheduled_time = models.CharField(max_length=30, null=True)

#     class Meta:
#         db_table = 'doctor_reschedulehistory'

# class DoctorSeniorDoctorAvailableTimeSlots(models.Model):
#     doctor = models.ForeignKey(DoctorDoctorProfiles, on_delete=models.CASCADE)
#     date = models.DateField()
#     time_slot = models.CharField(max_length=200)
#     is_active = models.IntegerField()

#     class Meta:
#         db_table = 'doctor_seniordoctoravailabletimeslots'

# class DoctorSrDoctorEngagement(models.Model):
#     appointment = models.ForeignKey(AnalysisAppointmentHeader, on_delete=models.SET_NULL, null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     time_slot = models.CharField(max_length=30)

#     class Meta:
#         db_table = 'doctor_srdoctorengagement'

# class DoctorTime(models.Model):
#     time = models.CharField(max_length=10, null=True)

#     class Meta:
#         db_table = 'doctor_time'

# class DoctorTimeSlots(models.Model):
#     time_slots = models.CharField(max_length=30)

#     class Meta:
#         db_table = 'doctor_timeslots'

# # Note: Django auth models (User, Group, Permission, etc.) are already built-in