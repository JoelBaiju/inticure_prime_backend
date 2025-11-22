from django.db.models import F
from rest_framework.decorators import api_view, permission_classes
from doctor.models import DoctorProfiles
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from doctor.models import DoctorProfiles,DoctorPaymentRules,DoctorSpecializations
from ..serializers import DoctorPaymentRuleSerializer
from ..serializers import DoctorProfileSerializer
from rest_framework import generics
from doctor.serializers import DoctorSpecializationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allow_prescription(request):
        doctor_id = request.GET.get('doctor_id')
        allow = request.GET.get('allow', 'true').lower() == 'true'
        try:
            doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
            if not allow:
                doctor.is_prescription_allowed = False
            else:
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
        
                
        # doctor_max_session_duration = (
        #     Specializations.objects
        #     .filter(doctor_specializations__doctor=doctor)
        #     .annotate(
        #         max_duration=Greatest(
        #             F('single_session_duration'),
        #             F('double_session_duration')
        #         )
        #     )
        #     .aggregate(overall_max=Max('max_duration'))['overall_max']
        #     or timedelta(0)
        # )
        
            
        doctor_max_session_duration = (
            Specializations.objects
            .filter(doctor_specializations__doctor=doctor)
            .aggregate(overall_max=Max('single_session_duration'))['overall_max']
            or timedelta(0)
        )
        # return Response({'available_dates':list(unique_dates) , "doctor_max_session_duration":doctor_max_session_duration + timedelta(minutes=10)}, status=status.HTTP_200_OK)
        return Response({'available_dates':list(unique_dates) , "doctor_max_session_duration":doctor_max_session_duration}, status=status.HTTP_200_OK)




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





@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def doctor_payment_assignment_detail(request, pk):
    try:
        assignment = DoctorPaymentRules.objects.get(pk=pk)
    except DoctorPaymentRules.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(DoctorPaymentRuleSerializer(assignment).data)

    elif request.method == 'PUT':
        serializer = DoctorPaymentRuleSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        assignment_id = assignment.id
        assignment.delete()
        return Response({"idToRemove": assignment_id}, status=200)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def doctor_payment_assignment_list_create(request):
    if request.method == 'GET':
        assignments = DoctorPaymentRules.objects.all()
        serializer = DoctorPaymentRuleSerializer(assignments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of assignments."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        added = []
        errors = []

        for entry in request.data:
            try:
                with transaction.atomic():
                    # Create context with request to pass to serializer
                    context = {'request': request}
                    serializer = DoctorPaymentRuleSerializer(
                        data=entry,
                        context=context
                    )
                    print('heres the serialier ')
                    # Perform validation and creation in one step
                    serializer.is_valid(raise_exception=True)

                    print('serializer valid')
                    obj = serializer.save()
                    print('serializer saved')
                    added.append(obj)
                    
            except Exception as e:
                error_detail = e.detail if hasattr(e, 'detail') else str(e)
                errors.append({
                    "entry": entry,
                    "message": error_detail
                })
                # Continue to next entry even if this one fails

        if errors:
            response_data = {
                "status": "partial_success" if added else "error",
                "added_assignments": DoctorPaymentRuleSerializer(added, many=True).data,
                "errors": errors
            }
            status_code = status.HTTP_207_MULTI_STATUS if added else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=status_code)

        return Response({
            "status": "success",
            "added_assignments": DoctorPaymentRuleSerializer(added, many=True).data
        }, status=status.HTTP_201_CREATED)
    


@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['POST'])
def doctor_payment_assignment_list_create_2(request):

    specialization = request.data.get('specialization_id')
    country_id = request.data.get('country_id')
    rules = request.data.get('rules')

    old_rules = DoctorPaymentRules.objects.filter(id__in=rules)

    to_create = []
    invalid_rules = []

    for rule_id in rules:
        old_rule = next((r for r in old_rules if r.id == rule_id), None)
        if not old_rule:
            invalid_rules.append({
                "rule_id": rule_id,
                "error": "Rule not found"
            })
            continue

        clone = DoctorPaymentRules(
            doctor=old_rule.doctor,
            general_rule=old_rule.general_rule,
            pricing_name=old_rule.pricing_name,
            session_count=old_rule.session_count,
            specialization_id=specialization,
            country_id=country_id,
            actual_price_single=old_rule.actual_price_single,
            actual_price_couple=old_rule.actual_price_couple,
            custom_doctor_fee_single=old_rule.custom_doctor_fee_single,
            custom_user_total_fee_single=old_rule.custom_user_total_fee_single,
            custom_doctor_fee_couple=old_rule.custom_doctor_fee_couple,
            custom_user_total_fee_couple=old_rule.custom_user_total_fee_couple,
        )
        to_create.append(clone)

    # Bulk create all cloned records in one go
    created = DoctorPaymentRules.objects.bulk_create(to_create)

    return Response({
        "message": "Completed with partial success" if invalid_rules else "All rules copied successfully",
        "created_rules": DoctorPaymentRuleSerializer(created, many=True).data,
        "invalid_rules": invalid_rules
    }, status=201 if created else 400)







class DoctorProfileUpdateView(generics.UpdateAPIView):
    queryset = DoctorProfiles.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'doctor_profile_id'



class DoctorSpecializationsView(generics.ListAPIView):
    
    serializer_class = DoctorSpecializationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.request.GET.get('doctor_id')
        return DoctorSpecializations.objects.filter(doctor__doctor_profile_id=doctor_id)