from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ..models import CustomerProfile
from analysis.models import AppointmentHeader
from ..serializers import CustomerDashboardSerializer , CustomerPreviousAppointmentsSerializer


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
            
         
            
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."}, 
                status=404
            )
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_previous_appointments(request):
    try:
        customer_profile = CustomerProfile.objects.get(user=request.user)
      
        serializer = CustomerPreviousAppointmentsSerializer(customer_profile)
        return Response(serializer.data)
    except CustomerProfile.DoesNotExist:
        return Response(
            {"error": "Customer profile not found."}, 
            status=404
        )