from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views as analysis_views


urlpatterns = [
    path('start_analysis/', analysis_views.StartAnalysisView.as_view(), name='StartAnalysisView'),
    path('phone_email_submission/', analysis_views.PhoneNumberOrEmailSubmissionView.as_view(), name='phone_email_submission'),
    path('phone_email_verification/', analysis_views.PhoneNumberOrEmailVerificationView.as_view(), name='phone_email_verification'),
    path('submit_gender_category/', analysis_views.SubmitGenderCategoryView.as_view(), name='submit_gender_category'),
    path('submit_questionnaire/', analysis_views.SubmitQuestionnaireView.as_view(), name='submit_questionnaire'),
    path('get_available_languages/', analysis_views.GetAvailableLanguages.as_view(), name='get_available_languages'),
    path('get_available_slots/', analysis_views.SlotsBooking.as_view(), name='get_available_slots'),
    path("doctor_details/", analysis_views.get_multiple_doctor_profiles),
    path('final_data_submit/', analysis_views.FinalSubmit.as_view(), name='submit_profile'),
    

]