from django.contrib import admin

# Register your models here.


from .models import LanguagesKnown

class LanguagesKnownAdmin(admin.ModelAdmin):
    list_display = ('id', 'language')

admin.site.register(LanguagesKnown, LanguagesKnownAdmin)