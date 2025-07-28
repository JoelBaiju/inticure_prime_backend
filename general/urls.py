from django.contrib import admin
from django.urls import path
from django.urls import include
from .finance.controllers import initiate_payment_controller 
from .finance.razorpay import verify_payment 
from .finance.stripe import verify_payment_stripe
from .views import consultation_cost_details_view


urlpatterns = [
    path('initiate_payment/', initiate_payment_controller, name='initiate_payment'),
    path("verify_payment/", verify_payment, name='verify_payment'),
    path("verify_payment_stripe/", verify_payment_stripe, name='verify_payment_stripe'),
    path('consultation-cost/', consultation_cost_details_view, name='consultation_cost_details'),

]