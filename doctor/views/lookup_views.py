from datetime import timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from administrator.models import LanguagesKnown, Countries, Specializations
from administrator.serializers import LanguagesKnownSerializer, CountriesSerializer, SpecializationsSerializer
from analysis.models import *
from customer.models import *
from django.shortcuts import get_object_or_404

from ..models import *
from ..serializers import *
from ..services.get_appointments_services import get_appointment_full_details_service
from ..services.availability_services import fetch_available_slots
from ..services.crud_services import *



@api_view(['GET'])
def get_all_languages(request):
    languages = LanguagesKnown.objects.all()
    serializer = LanguagesKnownSerializer(languages, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_countries(request):
    countries = Countries.objects.all()
    serializer = CountriesSerializer(countries, many=True)
    return Response(serializer.data)




from customer.services.doctor_availability_services import is_doctor_available_in_specialization
from inticure_prime_backend.settings import MAX_DOCTOR_AVAILABLITY_SEARCH_DAYS


@api_view(['GET'])
def get_all_specializations(request):
    session_type = request.GET.get('is_couple')
    appointment_id = request.GET.get('appointment_id')
    try:
        country = AppointmentHeader.objects.get(appointment_id=appointment_id).customer.country_details.country_name
        print(f"Session type received: {session_type}")
        if session_type and session_type.lower() == 'true':
            print(f"Fetching specializations with double session duration {session_type}")
            specializations = Specializations.objects.filter(
                double_session_duration__isnull=False,
                double_session_duration__gt=timedelta(seconds=0)
            )
        else:
            specializations = Specializations.objects.all()
        serializer = SpecializationsSerializer(specializations, many=True)
        for specialization in serializer.data:
            specialization['is_doctor_available'] = is_doctor_available_in_specialization(
                specialization['specialization_id'], 
                MAX_DOCTOR_AVAILABLITY_SEARCH_DAYS, 
                country
            )
        return Response(serializer.data)
    except Exception as e:
        print(f"Error fetching specializations: {e}")
        return Response({"error": f"An error occurred while fetching specializations.{e}"}, status=500)

@api_view(['GET'])
def get_all_specializations_without_availability(request):
    specializations = Specializations.objects.all()
    serializer = SpecializationsSerializer(specializations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def dotor_details_from_id(request):
    did = request.GET.get('did') 

    if not did:
        return Response({"error": "did is required"}, status=400)

    try:
        doctor = DoctorProfiles.objects.get(doctor_profile_id=did)
    
        if doctor.is_accepted:
            status='accepted'
        elif doctor.rejected:
            status='rejected'
        else :
            status = "pending"
        res = {
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "email_id": doctor.email_id,    
            "phone":doctor.whatsapp_number,
            "joined_date": doctor.joined_date,
            "status" : status                                                                                       
        }
        return Response(res, status=200)
    
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=400)
    

class AppointmentFullDetailsView(APIView):
    def get(self, request, appointment_id):
        try:
            response_data = get_appointment_full_details_service(appointment_id)
            return Response(response_data, status=status.HTTP_200_OK)
        except AppointmentHeader.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TestSubmitted(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        test_id = request.data.get('test')
        try:
            test = Prescribed_Tests.objects.get(id=test_id)
        except Prescribed_Tests.DoesNotExist:
            return Response({'error': 'Test not found.'}, status=status.HTTP_404_NOT_FOUND)
        test.submitted = True
        test.save()
        return Response({'message': 'Test submitted successfully'}, status=status.HTTP_200_OK)
    

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def get_available_slots_by_doctor(request):
    doctor_id = request.data.get("doctor_id")
    preferred_date = request.data.get("date")
    # cid    = request.data.get("cid")
    appointment_id = request.data.get('appointment_id')
    print("herererererererererererererererer")
    if not doctor_id:
        return Response({"error": "doctor_id is required"}, status=400)
    if not appointment_id:
        return Response({"error": "cid is required"}, status=400)
    try:
        appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
        customer = appointment.customer
        country = customer.country_details.country_name
    except CustomerProfile.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    try:
        results = fetch_available_slots(request.user, doctor_id, preferred_date,country)
        return Response({"slots": results}, status=200)
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_specializations(request):
    doctor = DoctorProfiles.objects.get(user = request.user)
    specialization = doctor.doctor_specializations.all()
    serializer = doctorSpecializationSerializer(specialization, many=True)
    return Response(serializer.data)




class Get_Prescriptions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_id = request.GET.get("customer")
        if not customer_id:
            return Response("customer id is required", status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor = DoctorProfiles.objects.get(user=request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        data, error = get_customer_prescriptions(customer_id , doctor)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)




class Get_Doctor_uploaded_files(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        appointment_id = request.GET.get("appointment_id")
        if not appointment_id:
            return Response("appointment_id is required", status=status.HTTP_400_BAD_REQUEST)
        try:
            files = CommonFileUploader.objects.filter(appointment__appointment_id=appointment_id , 
                                                      uploaded_by_doctor = True,
                                                      appointment__doctor__user = request.user)
            return Response(CommonFilesSerializer(files, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({f"error":" {e}"}, status=status.HTTP_404_NOT_FOUND)




