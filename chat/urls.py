from django.urls import path
from . import views

urlpatterns = [
    path('initiate_chat_customer_doctor/', views.initiate_chat_patient_doctor, name='initiate_chat'),
    path('join/', views.join_chat, name='join_session'),
    # path('join_d/', views.join_chat_doctor, name='join_session_doctor'),
    path('initiate_chat_patient_admin/', views.initiate_chat_patient_admin, name='initiate_chat_patient_admin'),
    path('initiate_chat_doctor_patient/',views.initiate_chat_doctor_patient , name='initiate_chat_doctor_patient'),
    path('initiate_chat_doctor_admin/', views.initiate_chat_doctor_admin, name='initiate_chat_doctor_admin'),

    path('active_sessions/', views.get_active_chat_sessions, name='get_active_chat_sessions'),
    path('session/<int:session_id>/detail/', views.get_chat_session_detail, name='get_chat_session_detail'),
]

