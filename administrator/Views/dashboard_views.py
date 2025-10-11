
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from doctor.models import *
from analysis.models import *
from customer.models import *


# class Admin_dashboard(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def get(self, request):
#         try:
#             total_doctors = Doctor.objects.count()
#             total_customers = Customer.objects.count()
#             total_appointments = Appointment.objects.count()
#             total_analyses = Analysis.objects.count()

#             data = {
#                 "total_doctors": total_doctors,
#                 "total_customers": total_customers,
#                 "total_appointments": total_appointments,
#                 "total_analyses": total_analyses,
#             }

#             return Response(data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)