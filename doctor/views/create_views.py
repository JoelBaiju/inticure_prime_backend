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
from django.utils import timezone
from datetime import timedelta

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
        try:
            validity_days = data.get('validity')
            if validity_days is None:
                return Response({'error': 'Validity period is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(validity_days, (int, float)):
                return Response({'error': 'Validity must be a number'}, status=status.HTTP_400_BAD_REQUEST)
            if validity_days <= 0:
                return Response({'error': 'Validity period must be positive'}, status=status.HTTP_400_BAD_REQUEST)
                
            data['validity'] = (timezone.now() + timedelta(days=validity_days)).date()
            serializer = PrescribedMedicationsCreateSerializer(data=data)
      
        except Exception as e:
            return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    




from django.utils import timezone

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_prescription_validity(request):
    try:
        appointment_id = request.data.get('appointment_id')
        valid_till_days = request.data.get('valid_till_days')
        valid_till = timezone.now().date() + timezone.timedelta(days=valid_till_days)
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

        validity , created = Prescrption_validity.objects.get_or_create(
            active=True,
            customer = appointment.customer,
            doctor = appointment.doctor 
        )
        validity.valid_till = valid_till
        validity.save()
        return Response({"message": "Prescription validity added successfully"}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_observation_notes(request):
    note_id = request.data.get('note_id')
    try:
        note = Observation_Notes.objects.get(id=note_id)
        if note.appointment.doctor.user != request.user:
            return Response({"error": "You do not have permission to delete this note"}, status=403)
        note.delete()
        return Response({"message": "Observation note deleted successfully"}, status=200)
    except Observation_Notes.DoesNotExist:
        return Response({"error": "Observation note not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_patient_notes(request):
    note_id = request.data.get('note_id')
    try:
        note = Notes_for_patient.objects.get(id=note_id)
        if note.doctor.user != request.user:
            return Response({"error": "You do not have permission to delete this note"}, status=403)
        note.delete()
        return Response({"message": "Patient note deleted successfully"}, status=200)
    except Notes_for_patient.DoesNotExist:
        return Response({"error": "Patient note not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

class EditObservationNotesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        note_id = request.data.get('note_id')
        new_note = request.data.get('note')
        try:
            note = Observation_Notes.objects.get(id=note_id)
            if note.appointment.doctor.user != request.user:
                return Response({"error": "You do not have permission to edit this note"}, status=403)
            note.note = new_note
            note.save()
            return Response({"message": "Observation note updated successfully","note":new_note}, status=200)
        except Observation_Notes.DoesNotExist:
            return Response({"error": "Observation note not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        

class EditPatientNotesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        note_id = request.data.get('note_id')
        new_note = request.data.get('note')
        try:
            note = Notes_for_patient.objects.get(id=note_id)
            if note.doctor.user != request.user:
                return Response({"error": "You do not have permission to edit this note"}, status=403)
            note.note = new_note
            note.save()
            return Response({"message": "Patient note updated successfully","note":new_note}, status=200)
        except Notes_for_patient.DoesNotExist:
            return Response({"error": "Patient note not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)