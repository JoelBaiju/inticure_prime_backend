"""
URL configuration for inticure_prime_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from administrator import urls as administrator_urls
from customer import urls as customer_urls
from doctor import urls as doctor_urls
from analysis import urls as analysis_urls
from general import urls as general_urls
from django.conf.urls.static import static
from  . import settings 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from general.views import Map_Meetings
from chat import urls as chat_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/', include(customer_urls)),
    path('doctor/', include(doctor_urls)),
    path('analysis/', include(analysis_urls)),
    path('general/', include(general_urls)),
    path('iadmin/', include(administrator_urls)),
    path('chat/',include(chat_urls)),


    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('meet/join/<str:attendee_meeting_id>/', Map_Meetings.as_view()),


]






urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)