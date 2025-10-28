
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from ..services.dashboard_services import get_dashboard_data
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

class Admin_dashboard(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            data = get_dashboard_data()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


from ..services.appointment_services import (
    get_admin_appointments_queryset,
    format_admin_appointment,
)


class AdminAppointmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return get_admin_appointments_queryset(self.request.query_params)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(qs)
        appointments = page if page is not None else qs

        results = [format_admin_appointment(a) for a in appointments]

        if page:
            return self.get_paginated_response(results)
        return Response(results)
