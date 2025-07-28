# urls.py

from django.urls import path
from .views import *
from analysis.views import SlotsBooking

urlpatterns = [
    path('languages/', get_all_languages, name='get_all_languages'),
    path('countries/', get_all_countries, name='get_all_countries'),
    path('specializations/', get_all_specializations, name='get_all_specializations'),
    path('details_with_id/', dotor_details_from_id, name='doctor_details_from_id'),
    path('doctor-profiles/create/', create_doctor_profile, name='create_doctor_profile'),
    path('login/', LoginView.as_view(), name='doctor_login'),
    path('verify_login/', Verify_Login.as_view(), name='doctor_login'),
    path('generate_slots/', create_calendar_and_slots_for_next_six_days, name='create_calendar_and_slots_for_next_six_days'),
    path("available_hours/", DoctorAvailableHoursView.as_view(), name="available-hours"),
    path("dashboard/", DoctorDashboardView.as_view(), name="available-slots"),
    path("available_slots/", SlotsBooking.as_view(), name="available-slots"),
    path("appointments/", GetAppointmentsView.as_view(), name="doctor-appointments"),
    path('refer/', ReferralCreateAPIView.as_view(), name='refer'),
    path('filter_doctors/', FilterDoctorsView.as_view(), name='filter_doctors'),
    path('doctor_slots/', Get_availableSlots_docid, name='doctor_slots'),
    path('create_appointment/', Create_NewAppointment, name='initiate_appointment'),
    path('customer_details_update/', Customer_details_update.as_view(), name='customer_details_update'),
]
