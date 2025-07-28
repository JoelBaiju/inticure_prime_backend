from django.contrib import admin
from .models import CustomerProfile

# Register your models here.
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age')
    
admin.site.register(CustomerProfile, CustomerProfileAdmin)