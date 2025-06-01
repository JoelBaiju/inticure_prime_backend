from django.contrib import admin
from .models import *


class CalendarAdmin(admin.ModelAdmin):
    list_display = [ 'date', 'day']

admin.site.register(Calendar, CalendarAdmin)

class GeneralTimeSlotsAdmin(admin.ModelAdmin):
    list_display = ['from_time', 'to_time']

admin.site.register(GeneralTimeSlots , GeneralTimeSlotsAdmin)

class DoctorAvailableSlotsAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'time_slot', 'is_available']

admin.site.register(DoctorAvailableSlots, DoctorAvailableSlotsAdmin)

class DoctorProfilesAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'qualification']

admin.site.register(DoctorProfiles, DoctorProfilesAdmin)

class DoctorLanguagesAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'language']   

admin.site.register(DoctorLanguages, DoctorLanguagesAdmin)