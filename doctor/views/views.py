from datetime import datetime, time, timedelta

import pytz
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from administrator.models import *
from analysis.models import *
from customer.models import *
from doctor.models import *
from doctor.services import (
    availability_services,
    dashboard_services,
)
from general.utils import (
    convert_local_dt_to_utc,
    get_doctor_from_user,
)
from general.tasks import send_reschedule_request_email_task

from ..models import *
from ..serializers import *
from ..services import (
    crud_services,
    get_appointments_services,
)
from ..services.crud_services import update_appointment_status
from ..services.earnings_services import get_doctor_earnings
from ..services.filter_doctor_service import DoctorFilterService
from ..services.payout_service import create_payout


from django.db.models import Max
from django.db.models.functions import Greatest

import logging
logger = logging.getLogger(__name__)




class   DoctorAvailableHoursView(APIView):
    """
    GET  /api/doctor/available-hours/?date=YYYY-MM-DD
    POST /api/doctor/available-hours/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor_profile = get_doctor_from_user(request.user)
        if not doctor_profile:
            return Response({"detail": "Doctor profile not found."}, status=404)

        date_str = request.GET.get("date")
        try:
            data = availability_services.get_available_hours(doctor_profile, date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        return Response(data, status=200)

    @transaction.atomic
    def post(self, request):
        doctor_profile = get_doctor_from_user(request.user)
        if not doctor_profile:
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


class CustomerDetailsUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        success, message = crud_services.update_customer_details(request.data)

        if not success:
            return Response({"error": message}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": message}, status=status.HTTP_200_OK)
    

class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = dashboard_services.get_doctor_or_none(request.user)
        if not doctor:
            return Response({"detail": "Doctor profile not found."}, status=404)

        data = dashboard_services.build_dashboard_response(doctor)
        return Response(data, status=200)


class GetAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = get_appointments_services.get_doctor_or_none(request.user)
        if not doctor:
            return Response({"detail": "Doctor profile not found."}, status=404)

        data = get_appointments_services.get_appointments_data(doctor)
        return Response(data, status=200)


class ReferralCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customers = request.data.get('customers', [])

        try:
            referral, serialized_data = crud_services.ReferralService.create_referral(
                user=request.user,
                data=request.data,
                customers=customers
            )
            return Response(
                {"message": "Referral created successfully.", "data": serialized_data},
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FilterDoctorsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            response_data = DoctorFilterService.filter_doctors(request.user, request.data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from general.notification_controller import send_doctor_reshceduled_notification
class AppointmentRescheduleView_Doctor(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        API to reschedule an appointment.
        Expects:
            - appointment_id: ID of the appointment to reschedule
        """
        data = request.data
        appointment_id = data.get('appointment')
        reason   = data.get('reason')
     
     
        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        if appointment.appointment_status in ['completed', 'cancelled' , 'rescheduled_by_doctor']:
            return Response({"error": "Cannot reschedule a completed or cancelled appointment."}, status=status.HTTP_400_BAD_REQUEST)
    
        # Update appointment details
        appointment.appointment_status = 'rescheduled_by_doctor'
        appointment.meeting_link = ''
   
        appointment.save()

        Reschedule_history.objects.create(appointment = appointment , reason = reason , initiated_by = 'doctor' )
        logger.debug("inside the doctor reshedule api bofore sending the notification ")
        send_doctor_reshceduled_notification(appointment_id=appointment.appointment_id)
        return Response({
            "message": "Appointment reschedule initiated.",
            "appointment_id": appointment.appointment_id
        }, status=status.HTTP_200_OK)


class Appointment_status_update(APIView):
    def post(self, request):
        completed = str(request.data.get("completed")).lower() == "true"
        reason = request.data.get("reason")
        appointment_id = request.data.get("appointment_id")

        return update_appointment_status(
            appointment_id=appointment_id,
            completed=completed,
            reason=reason
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_medicine(request):
    medicine_id = request.data.get('medicine_id')
    if not medicine_id:
        return Response('medicine id is required', status=status.HTTP_400_BAD_REQUEST)
    try:
        medicine = Prescribed_Medications.objects.get(id=medicine_id)
    except Prescribed_Medications.DoesNotExist:
        return Response('invalid medicine id',status=status.HTTP_400_BAD_REQUEST)
    medicine.is_active = False
    medicine.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def doctor_earnings(request):
    data = get_doctor_earnings(request.user)
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_payout(request):
    doctor = DoctorProfiles.objects.get(user=request.user)
    amount = request.data.get("amount")

    if not amount:
        return Response({"error": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        payout = create_payout(doctor, amount)
        return Response({"payout_id": payout.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payouts(request):
    doctor = DoctorProfiles.objects.get(user = request.user)
    payouts = Payouts.objects.filter(doctor = doctor)
    serializer = PayoutsSerializer(payouts, many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)



class DoctorBankAccountView(APIView):
    def get(self, request):
        doctor = DoctorProfiles.objects.get(user=request.user)
        bank_account = Doctor_Bank_Account.objects.filter(doctor=doctor)
        serializer = DoctorBankAccountSerializer(bank_account, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        doctor = DoctorProfiles.objects.get(user=request.user)
        bank_account = Doctor_Bank_Account.objects.filter(doctor=doctor)
        if bank_account.exists():
            return Response('Bank account already exists', status=status.HTTP_400_BAD_REQUEST)
        serializer = DoctorBankAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Available_dates(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        doctor = DoctorProfiles.objects.get(user=request.user)
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
                    F('double_session_duration')
                )
            )
            .aggregate(overall_max=Max('max_duration'))['overall_max']
            or timedelta(0)
        )
        return Response({'available_dates':list(unique_dates) , "doctor_max_session_duration":doctor_max_session_duration + timedelta(minutes=10)}, status=status.HTTP_200_OK)


class Specialization_already_referred(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        doctor = DoctorProfiles.objects.get(user=request.user)
        specialization = request.GET.get('specialization')
        customer = request.GET.get('customer')
        try:
            specialization = Specializations.objects.get(specialization=specialization)
            doctor = DoctorProfiles.objects.get(user=request.user)
            customer = CustomerProfile.objects.get(id=customer)
        except Specializations.DoesNotExist:
            return Response('Specialization does not exist', status=status.HTTP_400_BAD_REQUEST)
        except CustomerProfile.DoesNotExist:
            return Response('Customer does not exist', status=status.HTTP_400_BAD_REQUEST)
        except DoctorProfiles.DoesNotExist:
            return Response('Doctor does not exist', status=status.HTTP_400_BAD_REQUEST)


        referal_exists = Referral_customer.objects.filter(customer=customer , referral__doctor = doctor ,referral__specialization = specialization).exists()
        return Response({'referal_exists':referal_exists}, status=status.HTTP_200_OK)


class Available_packages(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        appointment = request.GET.get('appointment')
        referral_id = request.GET.get('referral')
        customer_id = request.GET.get('customer_id')
        is_couple   =True if request.GET.get('is_couple') and request.GET.get('is_couple') =="true" else False
        print(customer_id)
        try:
            if referral_id:
                referral = Referral.objects.get(id=referral_id)
            appointment = AppointmentHeader.objects.get(appointment_id=appointment)
            doctor = DoctorProfiles.objects.get(user=request.user)
            customer = CustomerProfile.objects.get(id=customer_id)
        except AppointmentHeader.DoesNotExist:
            return Response('Appointment does not exist', status=status.HTTP_400_BAD_REQUEST)
        except CustomerProfile.DoesNotExist:
            return Response('Customer does not exist', status=status.HTTP_400_BAD_REQUEST)
        except DoctorProfiles.DoesNotExist:
            return Response('You dont have the permission to access this api', status=status.HTTP_403_FORBIDDEN)
        except Referral.DoesNotExist:
            return Response('Referral does not exist', status=status.HTTP_400_BAD_REQUEST)


        package = Customer_Package.objects.filter(
            customer = customer,
            specialization = appointment.specialization,
            doctor = doctor,
            appointments_left__gt = 0,
            is_couple = is_couple,
            expires_on__gt = timezone.now()
        ).first()
        print(package)
        if package:
            return Response([],status=200)

        if appointment.specialization.is_prescription_allowed:
            country = Countries.objects.filter(country_name='India').first()
        else:
            country =   customer.country_details

        if referral_id:
            doctor = referral.doctor,
            specialization = referral.specialization
        else:
            doctor = doctor
            specialization = appointment.specialization
        try:
            packages = DoctorPaymentRules.objects.filter(
                doctor=doctor ,
                country=country,
                specialization=specialization,
                session_count__gt = 1
            )   
            serializer = DoctorPaymentRulesSerializer(packages, many=True)
        except Exception as e:
            return Response({'message':'An error occured while fetching packages','error':e}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)


class Suggest_package(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        customer_id = request.data.get('customer_id')
        package_id = request.data.get('package_id')
        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            package = DoctorPaymentRules.objects.get(id=package_id)
            doctor = DoctorProfiles.objects.get(user=request.user)
        except DoctorProfiles.DoesNotExist:
            return Response('You dont have the permission to access this api', status=status.HTTP_403_FORBIDDEN)
        except CustomerProfile.DoesNotExist:
            return Response('Customer does not exist', status=status.HTTP_400_BAD_REQUEST)
        except DoctorPaymentRules.DoesNotExist:
            return Response('Package does not exist', status=status.HTTP_400_BAD_REQUEST)

        Suggested_packages.objects.create(
            customer = customer,
            package = package,
            suggested_by = doctor,
        )
        return Response({'message':'Package suggested successfully'}, status=status.HTTP_200_OK)
    




