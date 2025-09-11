from django.contrib import admin
from .models import (
    Category, Questionnaire, Options, AppointmentHeader ,AnalysisSession,Referral ,Appointment_customers , Referral_customer , Meeting_Tracker , Prescribed_Medications,Reschedule_history,
    Prescribed_Tests,Notes_for_patient , Follow_Up_Notes ,Observation_Notes
)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']

admin.site.register(Category, CategoryAdmin)

class QuestionnaireAdmin(admin.ModelAdmin): 
    list_display = ['question']

admin.site.register(Questionnaire, QuestionnaireAdmin)

class OptionsAdmin(admin.ModelAdmin):
    list_display = ['option']

admin.site.register(Options, OptionsAdmin)

class AppointmentHeaderAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'customer', 'appointment_status', 'doctor','start_time', 'end_time']

admin.site.register(AppointmentHeader, AppointmentHeaderAdmin)

class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['id','token','phone_number','email','created_at',"session_status"]

admin.site.register(AnalysisSession, AnalysisSessionAdmin)


class ReferralsAdmin(admin.ModelAdmin):
    list_display = ['id'  , 'doctor' , 'referred_date' , 'referred_doctor' , 'referral_notes']

admin.site.register( Referral,ReferralsAdmin)

class AppointmentCustomerAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'customer']

admin.site.register(Appointment_customers, AppointmentCustomerAdmin)    



class ReferralCustomerAdmin(admin.ModelAdmin):
    list_display = ['referral', 'customer'] 

admin.site.register(Referral_customer, ReferralCustomerAdmin)



class MeetingTrackerAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment' , 'doctor_meeting_id' , 'customer_1_meeting_id']

admin.site.register(Meeting_Tracker, MeetingTrackerAdmin)


class PrescribedMedicationsAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment','doctor','customer']

admin.site.register(Prescribed_Medications, PrescribedMedicationsAdmin)


class PrescribedTestsAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment','doctor','customer']

admin.site.register(Prescribed_Tests, PrescribedTestsAdmin)

class NotesForPatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment','doctor','customer']

admin.site.register(Notes_for_patient, NotesForPatientAdmin)

class FollowUpNotesAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment','customer']

admin.site.register(Follow_Up_Notes, FollowUpNotesAdmin)    

class ObservationNotesAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment','customer']

admin.site.register(Observation_Notes, ObservationNotesAdmin)



admin.site.register(Reschedule_history)