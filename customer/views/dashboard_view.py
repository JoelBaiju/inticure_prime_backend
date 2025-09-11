from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import CustomerProfile
from analysis.models import AppointmentHeader
from ..serializers import CustomerDashboardSerializer


class CustomerDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerDashboardSerializer
    
    def get(self, request, *args, **kwargs):
        """
        API to get customer dashboard details
        """
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            serializer = self.get_serializer(customer_profile)
            
            # Get recent appointments for dashboard
            appointments = AppointmentHeader.objects.filter(
                customer=customer_profile
            ).order_by('-start_time')
            
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."}, 
                status=404
            )