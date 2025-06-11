from django.contrib import admin

# Register your models here.


from .models import LanguagesKnown, Countries

class LanguagesKnownAdmin(admin.ModelAdmin):
    list_display = ('id', 'language')

admin.site.register(LanguagesKnown, LanguagesKnownAdmin)


class CountriesAdmin(admin.ModelAdmin):
    list_display = ( 'country_name', 'currency', 'country_code')

admin.site.register(Countries, CountriesAdmin)
