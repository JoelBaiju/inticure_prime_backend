from django.contrib import admin
from .models import *

class DoctorProfilesAdmin(admin.ModelAdmin):
    list_display = ['doctor_profile_id','user' , 'is_accepted' , 'doctor_flag','gender', 'qualification']

admin.site.register(DoctorProfiles, DoctorProfilesAdmin)

class DoctorLanguagesAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'language']   

admin.site.register(DoctorLanguages, DoctorLanguagesAdmin)

class DoctorSpecializationAdmin(admin.ModelAdmin):
    list_display = ['doctor' , 'specialization']

admin.site.register(DoctorSpecializations , DoctorSpecializationAdmin)

class DoctorAvailableHoursAdmin(admin.ModelAdmin):
    list_display = [ 'doctor','doctor__doctor_profile_id' , 'start_time' , 'end_time' ]

admin.site.register(DoctorAvailableHours,DoctorAvailableHoursAdmin)


class DoctorAppointmentAdmin(admin.ModelAdmin):
    list_display = [ 'doctor' ,'appointment', 'specialization' , 'start_time' , 'end_time']

admin.site.register(DoctorAppointment , DoctorAppointmentAdmin)


class DoctorPaymentRulesAdmin(admin.ModelAdmin):
    list_display = [ 'doctor' ,'specialization' , 'country' , 'session_count']

admin.site.register(DoctorPaymentRules,DoctorPaymentRulesAdmin)


class DoctorPayoutsAdmin(admin.ModelAdmin):
    list_display = [ 'id'  ,'doctor'  , 'status' , 'amount' ,'initiated_at' , 'completed_at']

admin.site.register(Payouts,DoctorPayoutsAdmin)

