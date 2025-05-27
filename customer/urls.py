
from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views as customer_views
urlpatterns = [
    path('phone_email_verification/', customer_views.PhoneNumberOrEmailSubmissionView.as_view(), name='phone_email_verification'),
]
