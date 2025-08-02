from django.contrib import admin
from .models import CustomerProfile , Extra_questions , Extra_questions_answers

# Register your models here.
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age')
    
admin.site.register(CustomerProfile, CustomerProfileAdmin)

class Extra_questions_admin(admin.ModelAdmin):
    list_display = ('id','group','question')


admin.site.register(Extra_questions,Extra_questions_admin)


admin.site.register(Extra_questions_answers)