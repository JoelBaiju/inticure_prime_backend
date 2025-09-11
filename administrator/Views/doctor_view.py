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
  