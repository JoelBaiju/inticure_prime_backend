
from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views as customer_views
urlpatterns = [
    path('dashboard/', customer_views.CustomerDashboard.as_view(), name='customer_dashboard'),
    ]
