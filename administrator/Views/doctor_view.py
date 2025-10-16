from django.db.models import F
from rest_framework.decorators import api_view, permission_classes
from doctor.models import DoctorProfiles
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allow_prescription(request):
        doctor_id = request.GET.get('doctor_id')
        try:
            doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
            doctor.is_prescription_allowed = True
            doctor.save()
        except DoctorProfiles.DoesNotExist:
            return Response('doctor not found')
        return Response('prescription allowed')
  




from doctor.services import (
    availability_services,
    dashboard_services,
)
from rest_framework import status
from django.db import transaction
from rest_framework.views import APIView

class   DoctorAvailableHoursView(APIView):
    """
    GET  /api/doctor/available-hours/?date=YYYY-MM-DD
    POST /api/doctor/available-hours/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        did = request.GET.get('did')
        try:
            doctor_profile = DoctorProfiles.objects.get(doctor_profile_id=did)
        
        except DoctorProfiles.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=404)

        date_str = request.GET.get("date")
        try:
            data = availability_services.get_available_hours(doctor_profile, date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        return Response(data, status=200)

    @transaction.atomic
    def post(self, request):
        did = request.data.get('did')
        try:
            doctor_profile = DoctorProfiles.objects.get(doctor_profile_id=did)
        except DoctorProfiles.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=404)

        dates = request.data.get("dates", [])
        start_time_str = request.data.get("start_time")
        end_time_str = request.data.get("end_time")

        try:
            result = availability_services.save_availability_blocks(
                doctor_profile, dates, start_time_str, end_time_str
            )
        except availability_services.InvalidTimeFormat:
            return Response({"detail": "Invalid time format. Expected HH:MM."}, status=400)
        except availability_services.EndBeforeStart:
            return Response({"detail": "End time must be after start time."}, status=400)

        return Response(result, status=status.HTTP_201_CREATED)







from doctor.models import DoctorAvailableHours
from django.db.models import F, Max
from django.db.models.functions import Greatest
from django.utils import timezone
import pytz
from datetime import datetime, timedelta
from general.utils import convert_utc_to_local_return_dt , convert_local_dt_to_utc
from ..models import Specializations




class Available_dates(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        did = request.GET.get('did')
        try:
            doctor = DoctorProfiles.objects.get(doctor_profile_id=did)
        except DoctorProfiles.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=404)
        today_local = timezone.localtime(timezone.now(), timezone=pytz.timezone(doctor.time_zone)).replace(hour=0, minute=0, second=0, microsecond=0)
        local_date_time_str = datetime.combine(today_local, datetime.min.time()).strftime("%Y-%m-%dT%H:%M:%S")
        local_time_in_utc = convert_local_dt_to_utc(local_date_time_str , doctor.time_zone)
        
        available_dates = DoctorAvailableHours.objects.filter(
            doctor=doctor,
            start_time__gte=local_time_in_utc
        )
        start_times = available_dates.values_list('start_time', flat=True)
        start_times_converted_to_local_tz = [convert_utc_to_local_return_dt(start_time , doctor.time_zone) for start_time in start_times]
        unique_dates = [st.date() for st in start_times_converted_to_local_tz]
        unique_dates = list(set(unique_dates))
        unique_dates.sort()
        
                
        doctor_max_session_duration = (
            Specializations.objects
            .filter(doctor_specializations__doctor=doctor)
            .annotate(
                max_duration=Greatest(
                    F('single_session_duration'),
                    0
                    # F('double_session_duration')
                )
            )
            .aggregate(overall_max=Max('max_duration'))['overall_max']
            or timedelta(0)
        )
        # return Response({'available_dates':list(unique_dates) , "doctor_max_session_duration":doctor_max_session_duration + timedelta(minutes=10)}, status=status.HTTP_200_OK)
        return Response({'available_dates':list(unique_dates) , "doctor_max_session_duration":0}, status=status.HTTP_200_OK)




from doctor.services.availability_services import edit_availability_block


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_available_hours_view(request):
    try:
        did = request.data.get('did')
        doctor = DoctorProfiles.objects.get(doctor_profile_id=did)
        request.data["doctor_id"] = doctor.doctor_profile_id
        data = edit_availability_block(request.data)
        return Response(data, status=200)
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
