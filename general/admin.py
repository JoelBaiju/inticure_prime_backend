from django.contrib import admin
from .models import *

admin.site.register(Phone_OTPs)
admin.site.register(Email_OTPs)
admin.site.register(PreTransactionData)
admin.site.register(StripeTransactions)
admin.site.register(CommonFileUploader)