# urls.py

from django.urls import path
from analysis.views import SlotsBooking
from .views.views import *
from .views.lookup_views import *
from .views.auth_views import *
from .views.create_views import *


urlpatterns = [
    path('languages/', get_all_languages, name='get_all_languages'),
    path('countries/', get_all_countries, name='get_all_countries'),
    path('specializations/', get_all_specializations, name='get_all_specializations'),
    path('details_with_id/', dotor_details_from_id, name='doctor_details_from_id'),
    path('doctor-profiles/create/', create_doctor_profile, name='create_doctor_profile'),
    path('login/', LoginView.as_view(), name='doctor_login'),
    path('verify_login/', Verify_Login.as_view(), name='doctor_login'),
    path("available_hours/", DoctorAvailableHoursView.as_view(), name="available-hours"),
    path('available_dates/',Available_dates.as_view()),

    path("dashboard/", DoctorDashboardView.as_view(), name="available-slots"),

    path("available_slots/", SlotsBooking.as_view(), name="available-slots"),
    
    path("appointments/", GetAppointmentsView.as_view(), name="doctor-appointments"),
    path('refer/', ReferralCreateAPIView.as_view(), name='refer'),
    path('filter_doctors/', FilterDoctorsView.as_view(), name='filter_doctors'),
    
    path('doctor_slots/', get_available_slots_by_doctor, name='doctor_slots'),

    path('create_appointment/', create_new_appointment, name='initiate_appointment'),
    path('customer_details_update/', CustomerDetailsUpdate.as_view(), name='customer_details_update'),
    path('prescribe_medicine/', PrescribedMedicationsCreateView.as_view(), name='prescribe_medicine'),
    path('notes_for_patient/', AddNotesForPatientView.as_view(), name='notes_for_patient'),
    path('prescribe_tests/', PrescribedTestsCreateView.as_view(), name='prescribe_Tests'),
    path('test_submitted/', TestSubmitted.as_view(), name='test_submitted'),
    path('specialization_already_referred/', Specialization_already_referred.as_view(), name='specialization_already_referred'),

    path('obs_notes_add/', AddObservatioinNotesView.as_view(), name='obs_notes_add'),
    path('fp_notes_add/', AddFollowUpNotesView.as_view(), name='fp_notes_add'),
    path('appointment_details/<int:appointment_id>/', AppointmentFullDetailsView.as_view(), name='appointment_full_details'),
    path('reschedule/' , AppointmentRescheduleView_Doctor.as_view() , name='appointment reschedule'),
    path('status_update/',Appointment_status_update.as_view()),
    path('doctor_specializations/',get_doctor_specializations),
    path('prescriptions/',Get_Prescriptions.as_view()),
    path('deactivate_medicine/',deactivate_medicine),
    path('earnings/',doctor_earnings),
    path('request_payout/',request_payout),
    path('payouts/',get_payouts),
    path('bank_account/',DoctorBankAccountView.as_view()),
    path('available_packages/',Available_packages.as_view()),
    path('suggest_package/',Suggest_package.as_view()),





]
