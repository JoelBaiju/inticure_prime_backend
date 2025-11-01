from django.contrib import admin
from .models import *

admin.site.register(Phone_OTPs)
admin.site.register(Email_OTPs)
admin.site.register(PreTransactionData)
admin.site.register(StripeTransactions)
admin.site.register(RazorpayTransaction)
admin.site.register(Reminder_Sent_History)

@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    readonly_fields = ('transaction_date',)
    list_display = ('id', 'invoice_id', 'transaction_amount', 'payment_status', 'transaction_date')



class CommonFileUploaderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'appointment', 'common_file' , 'uploaded_on' , 'file_name' , 'uploaded_by_doctor')

admin.site.register(CommonFileUploader, CommonFileUploaderAdmin)

class AppointmentNotificationAdmin(admin.ModelAdmin):
    list_display = ('confirmation_admin_whatsapp_sent',   
                    'confirmation_customer_whatsapp_sent', 
                    'confirmation_doctor_whatsapp_sent',   
                    'confirmation_admin_email_sent',       
                    'confirmation_customer_email_sent',    
                    'confirmation_doctor_email_sent')

admin.site.register(AppointmentNotifications, AppointmentNotificationAdmin)