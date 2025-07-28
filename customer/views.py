from django.shortcuts import render
from rest_framework import generics
from .models import *
from django.contrib.auth.models import User
from general.models import *
from general.utils import *
from general.twilio import *
from rest_framework.response import Response
from rest_framework.views import APIView

from customer.serializers import CustomerProfileSerializer, CustomerDashboardSerializer

from analysis.models import AppointmentHeader


class CustomerDashboard(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    """
    API to get customer dashboard details
    """
    serializer_class = CustomerDashboardSerializer

    def get(self, request, *args, **kwargs):
        customer_profile = CustomerProfile.objects.get(user=self.request.user)
        serializer = self.get_serializer(customer_profile)
        
        appointments = AppointmentHeader.objects.filter(customer=customer_profile).order_by('-appointment_date', '-appointment_time')
        return Response(serializer.data)
    

