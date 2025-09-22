from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ..models import CustomerProfile
from analysis.models import AppointmentHeader ,Meeting_Tracker
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
    

from doctor.serializers import CommonFilesSerializer 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_files(request):
    """
    API to get customer files
    """
    appointment_id = request.GET.get('appointment_id', None)
    try:
        if appointment_id:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

        doctor_uploaded_files = appointment.common_files.filter(uploaded_by_doctor = True)
        doctor_uploaded_files = CommonFilesSerializer(doctor_uploaded_files, many=True)
        patient_uploaded_files = appointment.common_files.filter(uploaded_by_doctor = False)
        patient_uploaded_files = CommonFilesSerializer(patient_uploaded_files, many=True)
        return Response({
            "doctor_uploaded_files": doctor_uploaded_files.data,
            "patient_uploaded_files": patient_uploaded_files.data
        })
    except AppointmentHeader.DoesNotExist:
        return Response(
            {"error": "Appointment not found."}, 
            status=404
        )
    except Exception as e:
        return Response(
            {"error": "Error fetching customer files."}, 
            status=500
        )





@api_view(['GET'])
def get_meet_details_with_meet_id(request):
    """
    API to get meet details with meet id
    """
    meet_id = request.GET.get('meet_id', None)
    if not meet_id:
        return Response(
            {"error": "meet_id is required."}, 
            status=400
        )

    try:
        tracker = Meeting_Tracker.objects.get(customer_1_meeting_id=meet_id)    
    except Exception as e:
        return Response(
            {"error": "Meeting not found."}, 
            status=404
        )