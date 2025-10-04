from django.contrib import admin
from django.urls import path
from .views import *
from .Views.customer_views import *
from .Views.doctor_view import *
from .Views.finance_views import *

urlpatterns = [
   
    path('login/', AdminLoginView.as_view(), name='admin_login'),

    path('doc_details/', Doctor_Details.as_view(), name='doctor_Details'),
    path('doc_list/', Doctors_list.as_view(), name='doctor_Details'),
    path('doc/<int:pk>/', DoctorDetailAPIView.as_view(), name='doctor-detail'),
    path('doc/<int:doctor_profile_id>/', DoctorProfileUpdateView.as_view(), name='doctor-update'),
    path('update-flag-experience/<int:pk>/',UpdateDoctorFlagExperienceView.as_view(),name='update-doctor-flag-experience'),
    path('allow_prescription/', allow_prescription, name='allow_prescription'),

    path('doc/<int:pk>/accept/', DoctorAcceptAPIView.as_view(), name='doctor-accept'),
    path('doc/<int:pk>/reject/', DoctorRejectAPIView.as_view(), name='doctor-reject'),
    path('doc/available_dates/', Available_dates.as_view(), name='available_dates'),
    path('doc/available_hours/', DoctorAvailableHoursView.as_view(), name='available_hours'),
   
    path('specializations/', specializations_list_create, name='specializations-list-create'),
    path('specializations/<int:pk>/', specialization_detail, name='specialization-detail'),

    path('countries/', CountriesListCreateAPIView.as_view(), name='countries-list-create'),
    path('countries/<int:pk>/', CountriesDetailAPIView.as_view(), name='countries-detail'),
    
    path('languages/', LanguagesListCreateAPIView.as_view(), name='languages-list-create'),
    path('languages/<int:pk>/', LanguagesDetailAPIView.as_view(), name='languages-detail'),


    path("categories/", category_list_create),
    path("categories/<int:pk>/", category_detail),


    path("questionnaires/", questionnaire_list_create),  # supports ?gender=male&category=2
    path("questionnaires/<int:pk>/", questionnaire_detail),


    path("options/", option_list_create),
    path("options/<int:pk>/", option_detail),

    path("payment/general-rules/", general_payment_rule_list_create, name="general_payment_rule_list_create"),
    path("payment/general-rules/<int:pk>/", general_payment_rule_detail, name="general_payment_rule_detail"),

    # Doctor Payment Assignments
    path("payment/doctor-assignments/", doctor_payment_assignment_list_create, name="doctor_payment_assignment_list_create"),
    path("payment/doctor-assignments/<int:pk>/", doctor_payment_assignment_detail, name="doctor_payment_assignment_detail"),

    path('patient_list/', Patient_List_View.as_view(), name='patient_list'),
    path('customer_details/', CustomerProfileView.as_view(), name='customer_details'),
    path('customer_appointments/', CustomerAppointmentsView.as_view(), name='customer_appointments'),
    path('appointments/<int:appointment_id>/', AppointmentDetailsView.as_view(), name='appointment-details'),
    path('appointments/<int:appointment_id>/reschedule/', RescheduleAppointment.as_view(), name='reschedule-appointment'),
    path('appointments/<int:appointment_id>/cancel/', CancelAppointment.as_view(), name='cancel-appointment'),
    path('appointments/<int:appointment_id>/confirm/', ConfirmAppointment.as_view(), name='confirm-appointment'),
    path('appointments/<int:appointment_id>/complete/', CompleteAppointment.as_view(), name='complete-appointment'),
    path('create_appointment/', CreateAppointment.as_view(), name='create-appointment'),


    path('refunds/', get_refunds_view, name='get_refunds_view'),
    path('payouts/', get_payout_view, name='get_payout_view'),
    path('complete_payout/', complete_payout, name='complete_payout'),
    path('update_refund_status/', update_refund_status, name='update_refund_status'),





]
