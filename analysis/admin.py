from django.contrib import admin
from .models import Category, Questionnaire, Options, AppointmentHeader ,AnalysisSession,Referral

# Register your models here.

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
    list_display = ['appointment_id', 'customer', 'appointment_status', 'appointment_date', 'appointment_time', 'doctor']

admin.site.register(AppointmentHeader, AppointmentHeaderAdmin)

class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['id','token','phone_number','email','created_at',"session_status"]

admin.site.register(AnalysisSession, AnalysisSessionAdmin)


class ReferralsAdmin(admin.ModelAdmin):
    list_display = ['id' , 'customer' , 'doctor' , 'referred_date' , 'referred_doctor' , 'referral_notes']

admin.site.register( Referral,ReferralsAdmin)