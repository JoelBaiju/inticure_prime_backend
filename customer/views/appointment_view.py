from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from ..models import CustomerProfile
from analysis.models import AppointmentHeader
from doctor.models import DoctorAppointment
from general.models import PreTransactionData
from general.utils import (
    get_customer_timezone, convert_local_dt_to_utc, 
    convert_local_dt_to_utc_return_dt, get_current_time_in_utc_from_tz,
    is_doctor_available, track_map_meeting
)
from doctor.slots_service import get_available_slots
from ..services.appointment_service import AppointmentService
from ..services.notification_services import NotificationService
from ..utils.validators import AppointmentValidator


class DoctorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        doctor_id = request.query_params.get("doctor_id")
        date_str = request.query_params.get("date")
        is_couple = request.query_params.get("is_couple", "false").lower() == "true"

        if not doctor_id:
            return Response({"error": "doctor_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor_id = int(doctor_id)
        except ValueError:
            return Response({"error": "doctor_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        timeZone = get_customer_timezone(request.user)
        if not timeZone:
            return Response({"error": "Doctor time zone not set"}, status=400)

        base_date, end_of_base_date = get_current_time_in_utc_from_tz(timeZone)
        # base_date += timedelta(days=1)
        # end_of_base_date += timedelta(days=1)

        if date_str:
            try:
                preferred_dt_start = convert_local_dt_to_utc(f"{date_str}T00:00:00", timeZone)
                preferred_dt_end = convert_local_dt_to_utc(f"{date_str}T23:59:59", timeZone)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        else:
            preferred_dt_start = base_date
            preferred_dt_end = end_of_base_date

        results = get_available_slots(
            doctor_id=doctor_id,
            date_time_start=preferred_dt_start,
            date_time_end=preferred_dt_end,
            is_couple=is_couple,
            timezone_str=timeZone,
            buffer=timedelta(hours=6),
            country='India'
        )

        slots = results.get('slots', [])
        available_dates = results.get('available_dates', [])

        if not slots and available_dates:
            results = AppointmentService.find_next_available_slot(
                doctor_id, available_dates, timeZone, is_couple
            )

        return Response({"available_slots": results}, status=status.HTTP_200_OK)


class AppointmentRescheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        reason = request.data.get('reason')
        initiate = request.data.get('initiate')

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        if initiate:
            return self._initiate_reschedule(appointment, reason)
        else:
            return self._complete_reschedule(appointment, request.data.get('slot'), request.user)

    def _initiate_reschedule(self, appointment, reason):
        try:
            AppointmentValidator.validate_reschedule_eligibility(appointment)
            AppointmentService.initiate_reschedule(appointment, reason)
            return Response({
                "message": "Appointment reschedule initiated.",
                "appointment_id": appointment.appointment_id
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _complete_reschedule(self, appointment, slot_data, user):
        try:
            AppointmentValidator.validate_reschedule_status(appointment)
            AppointmentService.complete_reschedule(appointment, slot_data, user)
            return Response('Successfully rescheduled appointment', status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        reason = request.data.get('reason')

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
            AppointmentValidator.validate_cancellation_eligibility(appointment)
            AppointmentService.cancel_appointment(appointment, reason)
            
            return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_appointment_slot(request):

    appointment_id = request.data.get('appointment_id')
    slot = request.data.get('slot')
    
    # try:
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

    if request.user.is_superuser:
        customer = appointment.customer
    else:
        
        customer = CustomerProfile.objects.get(user=request.user)
    
    AppointmentService.book_appointment_slot(appointment, slot, customer)
    NotificationService.send_appointment_confirmation(appointment)
    
    return Response('Successfully booked appointment', status=status.HTTP_200_OK)
    # except (CustomerProfile.DoesNotExist, AppointmentHeader.DoesNotExist) as e:
    #     return Response({"error": "Profile or appointment not found."}, status=status.HTTP_404_NOT_FOUND)
    # except ValueError as e:
    #     print(e)
    #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relieve_package(request):
    appointment_id = request.GET.get('appointment')
    
    try:
        appointment = AppointmentService.relieve_appointment_package(appointment_id)
        return Response({'message': 'Package relieved successfully'}, status=status.HTTP_200_OK)
    except AppointmentHeader.DoesNotExist:
        return Response({'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    





