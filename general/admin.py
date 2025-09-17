from django.contrib import admin
from .models import *

admin.site.register(Phone_OTPs)
admin.site.register(Email_OTPs)
admin.site.register(PreTransactionData)
admin.site.register(StripeTransactions)

class CommonFileUploaderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'appointment', 'common_file' , 'uploaded_on' , 'file_name' , 'uploaded_by_doctor')

admin.site.register(CommonFileUploader, CommonFileUploaderAdmin)
