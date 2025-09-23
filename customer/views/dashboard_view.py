from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ..models import CustomerProfile
from analysis.models import AppointmentHeader ,Meeting_Tracker
from ..serializers import CustomerDashboardSerializer , CustomerPreviousAppointmentsSerializer

import logging
logger = logging.getLogger(__name__)

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



from general.utils import convert_local_dt_to_utc_return_dt

# @api_view(['GET'])
# def get_meet_details_with_meet_id(request):
#     """
#     API to get meet details with meet id
#     """
#     meet_id = request.GET.get('meet_id', None)
#     logger.debug(meet_id)
#     if not meet_id:
#         return Response(
#             {"error": "meet_id is required."}, 
#             status=400
#         )
#     try:
        
#         # try:
#         #     tracker = Meeting_Tracker.objects.get(customer_1_meeting_id=meet_id) 
#         #     is_customer_1 = True
#         # except Meeting_Tracker.DoesNotExist:
#         #     try :
#         #         tracker = Meeting_Tracker.objects.get(customer_2_meeting_id = meet_id)
#         #         is_customer_1 = False
#         #     except Meeting_Tracker.DoesNotExist:
#         #         return Response(
#         #             {"error": "Meeting not found."}, 
#         #             status=404
#         #         )
#         from django.db.models import Q

#         tracker = Meeting_Tracker.objects.filter(
#             Q(customer_1_meeting_id=meet_id) | Q(customer_2_meeting_id=meet_id)
#         ).first()

#         if not tracker:
#             return Response({"error": "Meeting not found."}, status=404)
#         doctor = tracker.appointment.doctor
#         appointment = tracker.appointment
        
         
#         if is_customer_1:
#             date_time =convert_local_dt_to_utc_return_dt(appointment.start_time, tracker.customer_1.time_zone)
#             data = {
#                 "doctor_name" : f"{doctor.salutation} {doctor.first_name}",
#                 "specialization" : appointment.specialization.specialization,
#                 "time" : date_time.time(),
#                 "date":date_time.date(),
#             }
        
#         elif not is_customer_1:
#             date_time =convert_local_dt_to_utc_return_dt(appointment.start_time, tracker.customer_2.time_zone)
#             data = {
#                 "doctor_name" : f"{doctor.salutation} {doctor.first_name}",
#                 "specialization" : appointment.specialization.specialization,
#                 "time" : date_time.time(),
#                 "date":date_time.date(),
#             }
#         return Response(data)

#     except Exception as e:
#         return Response(
#             {"error": "Meeting not found."}, 
#             status=404
#         )








from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_meet_details_with_meet_id(request):
    """
    API to get meet details with meet_id
    """
    meet_id = request.GET.get('meet_id')
    logger.debug(meet_id)
    if not meet_id:
        return Response({"error": "meet_id is required."}, status=400)

    try:
        tracker = (
            Meeting_Tracker.objects
            .filter(Q(customer_1_meeting_id=meet_id) | Q(customer_2_meeting_id=meet_id))
            .select_related("appointment__doctor", "appointment__specialization")
            .first()
        )

        if not tracker:
            return Response({"error": "Meeting not found."}, status=404)

        # ✅ Determine which customer matched
        is_customer_1 = tracker.customer_1_meeting_id == meet_id

        doctor = tracker.appointment.doctor
        appointment = tracker.appointment

        if is_customer_1:
            date_time = convert_local_dt_to_utc_return_dt(
                appointment.start_time, tracker.customer_1.time_zone
            )
        else:
            date_time = convert_local_dt_to_utc_return_dt(
                appointment.start_time, tracker.customer_2.time_zone
            )

        data = {
            "doctor_name": f"{doctor.salutation} {doctor.first_name}",
            "specialization": appointment.specialization.specialization,
            "time": date_time.time(),
            "date": date_time.date(),
        }
        return Response(data)

    except Exception as e:
        logger.exception("Error fetching meeting details")
        return Response({"error": "Meeting not found."}, status=404)
