from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from analysis.models import *
from ..models import *
from customer.models import *
from ..serializers import *
from rest_framework.permissions import IsAuthenticated
from ..services.crud_services import create_new_appointment_service
from rest_framework.decorators import api_view, permission_classes
from ..services.availability_services import edit_availability_block


class PrescribedMedicationsCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
     
        try:
            doctor = DoctorProfiles.objects.get(user = request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({'error': 'Doctor invalid not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        print(doctor.doctor_profile_id)
        data['doctor'] = doctor.doctor_profile_id

        serializer = PrescribedMedicationsCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Medication added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrescribedTestsCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):

        try:
            doctor = DoctorProfiles.objects.get(user = request.user)
        except DoctorProfiles.DoesNotExist:
            return Response({'error': 'Doctor invalid not found.'}, status=status.HTTP_404_NOT_FOUND)


        data = request.data.copy()
        print(doctor.doctor_profile_id)
        data['doctor'] = doctor.doctor_profile_id

        serializer = PrescribedTestsCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'test added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddObservatioinNotesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')
        note = request.data.get('note')
        customer_id = request.data.get('customer')


        if not appointment_id or not note:
            return Response({'error': 'appointment and note are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = CustomerProfile.objects.get(id=customer_id)
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except CustomerProfile.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)


        data = Observation_Notes.objects.create(appointment = appointment , note = note , customer = customer)


        return Response({'message': 'Note Added successfully',"note":note}, status=status.HTTP_201_CREATED)



class AddFollowUpNotesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')
        note = request.data.get('note')
        customer_id = request.data.get('customer')
        if not appointment_id or not note:
            return Response({'error': 'appointment and note are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
            customer = CustomerProfile.objects.get(id=customer_id)
        except CustomerProfile.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
       
        data = Follow_Up_Notes.objects.create(appointment = appointment , note = note , customer = customer)


        return Response({'message': 'Note Added successfully',"note":note}, status=status.HTTP_201_CREATED)



class AddNotesForPatientView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        appointment_id = request.data.get('appointment')
        customer_id = request.data.get('customer')
        note = request.data.get('note')

        if not appointment_id or not note:
            return Response({'error': 'appointment and note are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
            customer = CustomerProfile.objects.get(id=customer_id)
        except AppointmentHeader.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except CustomerProfile.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = Notes_for_patient.objects.create(appointment = appointment , note = note , customer = customer , doctor = appointment.doctor)

        return Response({'message': 'Note Added successfully',"note":note}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_new_appointment(request):
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
    


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_available_hours_view(request):
    try:
        doctor = DoctorProfiles.objects.get(user=request.user)
        request.data["doctor_id"] = doctor.doctor_profile_id
        data = edit_availability_block(request.data)
        return Response(data, status=200)
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        if uploaded_file.size > 10 * 1024 * 1024:  # 10 MB limit
            return Response({'error': 'File size exceeds 10 MB limit'}, status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            return Response({'error': 'Invalid file type. Only PDF and image files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.POST.get('appointment_id') or not request.POST.get('file_name'):
            return Response({'error': 'appointment_id and file_name are required.'}, status=status.HTTP_400_BAD_REQUEST)
        file_instance = CommonFileUploader.objects.create(
            appointment_id=request.POST.get('appointment_id'),
            common_file=uploaded_file,
            file_name=request.POST.get('file_name'),
        )

        return Response({'message': 'File uploaded successfully', 'file_id': file_instance.id}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)