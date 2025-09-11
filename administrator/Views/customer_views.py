from calendar import c
from math import fabs
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from customer.models import *
from analysis.models import * 
from ..serializers import *
from customer.serializers import CustomerDashboardSerializer
from django.db.models import Q

from analysis.models import AppointmentHeader
from ..serializers import AppointmentSerializer
from customer.services.appointment_service import AppointmentService
from customer.services.profile_service import ProfileService
from customer.utils.validators import AppointmentValidator,ProfileValidator
from ..services.appointment_services import create_new_appointment_service



class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        search_query = request.query_params.get('search', '')
        
        if customer_id:
            try:
                customer = CustomerProfile.objects.get(id=customer_id)
                serializer = CustomerProfileSerializer(customer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomerProfile.DoesNotExist:
                return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        elif search_query:
            customers = CustomerProfile.objects.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(whatsapp_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            serializer = CustomerProfileSerializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Please provide a 'customer_id' or 'search' query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        customer_id = request.query_params.get('customer_id')
        try:
            customer = CustomerProfile.objects.get(id=customer_id)
        except CustomerProfile.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerProfileSerializerFull(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomerAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            customer_data = CustomerDashboardSerializer(customer).data
            return Response(customer_data, status=status.HTTP_200_OK)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointments not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class AppointmentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        








class AppointmentActions(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        actions = {
            'reschedule'    : False,
            'cancel'        : False,
            'confirm'       : False,
            'complete'      : False,
            'add_partner'   : False,
            "add_slot"      : False,
        }



class RescheduleAppointment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, appointment_id):
        slot_data = request.data.get('slot')
        is_admin = False
        if request.user.is_superuser:
            is_admin = True
            

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return
    
        try:
            AppointmentService.complete_reschedule(appointment, slot_data, appointment.customer.user, is_admin)
            return Response('Successfully rescheduled appointment', status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request , appointment_id):
        reason = request.data.get('reason',None)
        is_admin = False
        if request.user.is_superuser:
            is_admin = True
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            AppointmentService.cancel_appointment(appointment, reason, is_admin)
            return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        




from customer.utils.validators import AppointmentValidator
class ConfirmAppointment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, appointment_id):
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            if appointment.is_couple and not appointment.customer.partner:
                return Response({"message":"Appointment not confirmed add partner" , "add_partner":True}, status=status.HTTP_200_OK)
            if not AppointmentService.confirm_appointment(appointment):
                return Response({"message":"Appointment not confirmed select slots" , "select_slots":True}, status=status.HTTP_200_OK)
            return Response({"message": "Appointment confirmed successfully.", "select_slots":False , "add_partner":False}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        




class CompleteAppointment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, appointment_id):
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            if not AppointmentService.complete_appointment(appointment):
                return Response({"message":"Appointment not completed" , "complete":True}, status=status.HTTP_200_OK)
            return Response({"message": "Appointment completed successfully.", "complete":False}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    




class CreateAppointment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            appointment, serialized_data = create_new_appointment_service(request.data)
            return Response(
                {"message": "Appointment successfully booked", "appointment": serialized_data},
                status=200,
            )
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Ongoing appointment not found"}, status=400)
        except Specializations.DoesNotExist:
            return Response({"error": "Specialization not found"}, status=400)
        except DoctorProfiles.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)




class PendingRefunds(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            appointments = AppointmentHeader.objects.filter(appointment_status = "confirmed")
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)