from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ..models import CustomerProfile, Suggested_packages
from administrator.models import Specializations
from doctor.models import DoctorProfiles, DoctorPaymentRules
from analysis.models import (
    Prescribed_Medications, Prescribed_Tests, 
    Notes_for_patient, Follow_Up_Notes
)
from ..serializers import (
    PrescribedMedicationsSerializer, PrescribedTestsSerializer,
    NotesForPatientSerializer, Followup_notes_serializer,
    PatientSerializer, SpecializationsSerializerFull
)
from doctor.serializers import DoctorPaymentRulesSerializer
from ..services.prescription_services import PrescriptionService
from ..services.doctor_availability_services import get_specializations_service
from ..utils.pdf_generator import PrescriptionPDFGenerator


class PrescriptionsView(APIView):
    def get(self, request):
        """Get customer prescriptions grouped by doctor"""
        customer_id = request.GET.get('cid')
        
        try:
            customer = CustomerProfile.objects.get(id=customer_id)
        except CustomerProfile.DoesNotExist:
            return Response(
                {'error': 'Invalid customer ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        prescription_data = PrescriptionService.get_customer_prescriptions(customer)
        customer_data = PatientSerializer(customer).data

        return Response({
            "prescriptions": prescription_data,
            "patient_first_name": customer.user.first_name,
            "patient_last_name": customer.user.last_name,
            "patient_details": customer_data
        })


# class PrescriptionPDFView(APIView):
#     def get(self, request):
#         """Generate prescription PDF for customer and doctor"""
#         customer_id = request.GET.get('cid')
#         doctor_id = request.GET.get('did')
        
#         try:
#             customer = CustomerProfile.objects.get(id=customer_id)
#             doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
#         except (CustomerProfile.DoesNotExist, DoctorProfiles.DoesNotExist):
#             return HttpResponse(
#                 '<h1>Error: Invalid customer or doctor ID</h1>', 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             context = PrescriptionService.generate_prescription_context(customer, doctor)
#             pdf = PrescriptionPDFGenerator.generate_prescription_pdf(context)
            
#             response = HttpResponse(pdf, content_type='application/pdf')
#             response['Content-Disposition'] = 'inline; filename="prescription.pdf"'
#             return response
#         except Exception as e:
#             return HttpResponse(
#                 f'<h1>Error generating PDF: {str(e)}</h1>', 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status

class PrescriptionPDFView(APIView):
    permission_classes = [IsAuthenticated] 
    renderer_classes = []    # ⬅️ disables DRF rendering

    def get(self, request):
        customer_id = request.GET.get('cid')
        doctor_id = request.GET.get('did')

        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
        except (CustomerProfile.DoesNotExist, DoctorProfiles.DoesNotExist):
            return HttpResponse(
                '<h1>Error: Invalid customer or doctor ID</h1>',
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            context = PrescriptionService.generate_prescription_context(customer, doctor)
            pdf = PrescriptionPDFGenerator.generate_prescription_pdf(context)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="prescription.pdf"'
            return response
        except Exception as e:
            return HttpResponse(
                f'<h1>Error generating PDF: {str(e)}</h1>',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def get_specializations(request):
    country = request.GET.get('country')
    specializations = get_specializations_service(country)
    return Response(specializations , status=status.HTTP_200_OK)


@api_view(['GET'])
def get_specialization_by_id(request):
    """Get specialization details by ID"""
    specialization_id = request.GET.get('specialization_id')
    
    try:
        specialization = Specializations.objects.get(specialization_id=specialization_id)
        serializer = SpecializationsSerializerFull(specialization)
        return Response(
            {'specialization': serializer.data}, 
            status=status.HTTP_200_OK
        )
    except Specializations.DoesNotExist:
        return Response(
            {'message': 'Specialization not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_packages(request):
    """Get all packages for a doctor and specialization"""
    doctor_id = request.GET.get('doctor_id')
    specialization_id = request.GET.get('specialization_id')
    
    try:
        customer = CustomerProfile.objects.get(user=request.user)
        doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
        specialization = Specializations.objects.get(specialization_id=specialization_id)
        
        packages_data = PrescriptionService.get_doctor_packages(doctor, specialization, customer)
        
        return Response({'packages': packages_data}, status=status.HTTP_200_OK)
    except (CustomerProfile.DoesNotExist, DoctorProfiles.DoesNotExist, Specializations.DoesNotExist):
        return Response(
            {'message': 'Customer, doctor, or specialization not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )