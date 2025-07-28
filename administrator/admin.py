from django.contrib import admin

# Register your models here.


from .models import *


class LanguagesKnownAdmin(admin.ModelAdmin):
    list_display = ('id', 'language')

admin.site.register(LanguagesKnown, LanguagesKnownAdmin)


class CountriesAdmin(admin.ModelAdmin):
    list_display = ( 'country_name', 'currency', 'country_code')

admin.site.register(Countries, CountriesAdmin)

class SpcializationAdmin(admin.ModelAdmin):
    list_display = ('specialization_id' , 'specialization')

admin.site.register(Specializations,SpcializationAdmin)

class GeneralPaymentRulesAdmin(admin.ModelAdmin):
    list_display = ['country' , 'specialization', 'experience' ,'session_count']

admin.site.register(GeneralPaymentRules , GeneralPaymentRulesAdmin)