
from django.contrib import admin
from django.urls import path
from django.urls import include
from .views.appointment_view import *
from .views.dashboard_view import *
from .views.prescription_view import *
from .views.profile_view import *
urlpatterns = [
    path('dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('previous_appointments/', get_previous_appointments, name='customer_previous_appointments'),
    path('doctors_slots/', DoctorAvailabilityView.as_view()),
    path('contact_details/',ContactDetailsView.as_view()),
    path('reschedule/',AppointmentRescheduleView.as_view()),
    path('add_slot/',add_appointment_slot ),
    path('cancel_appointment/',CancelAppointmentView.as_view()),
    path('create_partner/', create_partner, name='create_partner'),
    path('partner_exists/', PartnerExistenceView.as_view(), name='check_partner_exists'),
    path('get_prescriptions/', PrescriptionsView.as_view()),
    path('get_specializations/', get_specializations),
    path('relieve_package/', relieve_package),
    path('download_prescriptions/',PrescriptionPDFView.as_view()),
    path('get_specialization_from_id/',get_specialization_by_id),
    path('get_all_packages/',get_doctor_packages),
    path('edit/', CustomerProfileUpdateView.as_view()),
    path('change_whatsapp_email/', WhatsappNumberOrEmailChangeView.as_view()),
    path('change_whatsapp_email/verify/', VerifyWhatsappNumberOrEmailChangeView.as_view()),
    path('add_customer_country/', add_customer_country),
    path('get_patient_details/', PatientDetailsFromPhoneEmailView.as_view()),
    path('connect_partner/', ConnectPartnersView.as_view()),
    ]
