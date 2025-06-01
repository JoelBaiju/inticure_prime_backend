from django.contrib import admin

# Register your models here.
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age')
    