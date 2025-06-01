from django.contrib import admin
from .models import Category, Questionnaire, Options

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']

admin.site.register(Category, CategoryAdmin)

class QuestionnaireAdmin(admin.ModelAdmin): 
    list_display = ['question']

admin.site.register(Questionnaire, QuestionnaireAdmin)

class OptionsAdmin(admin.ModelAdmin):
    list_display = ['option']

admin.site.register(Options, OptionsAdmin)