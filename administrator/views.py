# Python standard
from datetime import datetime

# Django core
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import transaction

# DRF core
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

# Local models
from doctor.models import (
    DoctorProfiles,
    DoctorSpecializations,
    DoctorPaymentRules
)
from general.emal_service import send_doctor_status_email
from .models import (
    Specializations,
    Countries,
    GeneralPaymentRules,
    LanguagesKnown
)
from analysis.models import AppointmentHeader, Options, Questionnaire, Category

# Local serializers
from .serializers import (
    DoctorProfileSerializer,
    SpecializationsSerializerFull,
    CountriesSerializer,
    GeneralPaymentRuleSerializer,
    DoctorPaymentRuleSerializer,
    LanguagesKnownSerializer,
    SpecializationsSerializerWrite
)



from analysis.models import Options , Questionnaire , Category
from analysis.serializers import QuestionnaireSerializerWithOptions ,OptionsSerializer , CategorySerializer





from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import DoctorProfileSerializer_update






class AdminLoginView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response( 'Username and password are required.',status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'verified': True,
                'message': 'User Verified',
                'user_id': user.id,
                'sessionid': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({
                'verified': False,
                'message': 'Invalid username or password.'
            }, status=status.HTTP_400_BAD_REQUEST)
        






class Doctor_Details(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get(self,request):
        total_approved = DoctorProfiles.objects.filter(is_accepted=1).count()
        total_female = DoctorProfiles.objects.filter(gender__iexact='female').count()
        total_male = DoctorProfiles.objects.filter(gender__iexact='male').count()
        pending_applications = DoctorProfiles.objects.filter(is_accepted=False,rejected=False).count()
        rejected_applications = DoctorProfiles.objects.filter(rejected=True).count()

        senior_doctors = DoctorProfiles.objects.filter(doctor_flag='senior',is_accepted = True).count()
        junior_doctors = DoctorProfiles.objects.filter(doctor_flag='junior',is_accepted = True).count()

        return Response({
            'total_approved_doctors': total_approved,
            'total_female_doctors': total_female,
            'total_male_doctors': total_male,
            'pending_applications': pending_applications,
            'rejected_applications': rejected_applications,
            'total_senior_doctors': senior_doctors,
            'total_junior_doctors': junior_doctors,
        })
    






class DoctorPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100





class Doctors_list(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get(self, request):
        filter = request.GET.get('status')
    
        if filter == 'pending':
            queryset = DoctorProfiles.objects.filter(is_accepted=False , rejected = False)
        elif filter == 'rejected':
            queryset = DoctorProfiles.objects.filter(rejected = True)
        else:
            print("inside verified")
            queryset = DoctorProfiles.objects.filter(is_accepted=True)

        paginator = DoctorPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = DoctorProfileSerializer(paginated_queryset, many=True)
        # serializer = DoctorProfileSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
        # return Response(serializer.data)
    

class DoctorDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfiles, pk=pk)
        serializer = DoctorProfileSerializer(doctor)
        return Response(serializer.data)











class UpdateDoctorFlagExperienceView(UpdateAPIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    queryset = DoctorProfiles.objects.all()
    
    def put(self, request, pk):
        experience = request.data.get('experience')
        doctor_flag = request.data.get('doctor_flag')

        if not pk or not experience or not doctor_flag:
            return Response({'error': 'experience, doctor_flag are required.'}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(DoctorProfiles, pk=pk)
        doctor.experience = experience
        doctor.doctor_flag = doctor_flag
        doctor.save()

        return Response({'status': 'Doctor flag and experience updated','experience':experience,'flag':doctor_flag},
                         status=status.HTTP_200_OK)    


class DoctorAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def put(self, request, pk):
      
        if not pk  :
            return Response({'error': 'experience, doctor_flag are required.'}, status=status.HTTP_400_BAD_REQUEST)
        doctor = get_object_or_404(DoctorProfiles, pk=pk)
        if doctor.doctor_flag is None or doctor.experience is None:
            return Response({'error': 'Doctor flag and experience must be set before accepting.'}, status=status.HTTP_400_BAD_REQUEST)
        doctor.is_accepted = True
        doctor.rejected = False
        doctor.rejection_reason = None
        doctor.accepted_date = timezone.now()
        doctor.save()
        send_doctor_status_email(
           doctor_id=doctor.doctor_profile_id
        )   

        return Response({'status': 'Doctor accepted'}, status=status.HTTP_200_OK)
    

from general.tasks import send_doctor_status_email_task
class DoctorRejectAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def put(self, request, pk):
        reason = request.data.get('rejection_reason')
        if not reason:
            return Response({'error': 'Rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

        doctor = get_object_or_404(DoctorProfiles, pk=pk)
        doctor.rejected = True
        doctor.is_accepted = False
        doctor.rejection_reason = reason
        doctor.save()
        send_doctor_status_email_task.delay(
            doctor_id = doctor.id,
        )
        return Response({'status': 'Doctor rejected', 'reason': reason}, status=status.HTTP_200_OK)








@permission_classes([IsAuthenticated,IsAdminUser])
@api_view(['GET', 'POST'])
def specializations_list_create(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        specializations = Specializations.objects.all()
        if search_query:
            specializations = specializations.filter(specialization__icontains=search_query)
        serializer = SpecializationsSerializerFull(specializations, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        print('Received data:', request.data)
        print('speialization:', request.data.get('specialization'))
        print('description:', request.data.get('description'))
        print('double_session_duration:', request.data.get('double_session_duration'))
        print('single_session_duration:', request.data.get('single_session_duration'))
        serializer = SpecializationsSerializerWrite(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated,IsAdminUser])
@api_view(['GET', 'PUT', 'DELETE'])
def specialization_detail(request, pk):
    try:
        specialization = Specializations.objects.get(pk=pk)
    except Specializations.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SpecializationsSerializerFull(specialization)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SpecializationsSerializerWrite(specialization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        specialization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)







class CountriesListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get(self, request):
        search_query = request.GET.get('search', '')
        countries = Countries.objects.all()
        if search_query:
            countries = countries.filter(country_name__icontains=search_query)
        serializer = CountriesSerializer(countries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CountriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CountriesDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get_object(self, pk):
        return get_object_or_404(Countries, pk=pk)

    def get(self, request, pk):
        country = self.get_object(pk)
        serializer = CountriesSerializer(country)
        return Response(serializer.data)

    def put(self, request, pk):
        country = self.get_object(pk)
        serializer = CountriesSerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        country = self.get_object(pk)
        country.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





class LanguagesListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated ,IsAdminUser]
    def get(self, request):
        search_query = request.GET.get('search', '')
        languages = LanguagesKnown.objects.all()
        if search_query:
            languages = languages.filter(language__icontains=search_query)
        serializer = LanguagesKnownSerializer(languages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LanguagesKnownSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LanguagesDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get_object(self, pk):
        return get_object_or_404(LanguagesKnown, pk=pk)

    def get(self, request, pk):
        language = self.get_object(pk)
        serializer = LanguagesKnownSerializer(language)
        return Response(serializer.data)

    def put(self, request, pk):
        language = self.get_object(pk)
        serializer = LanguagesKnownSerializer(language, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        language = self.get_object(pk)
        language.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






# ======================================================================================




# ----------- CATEGORY CRUD -----------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(CategorySerializer(category).data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=204)


# ----------- QUESTIONNAIRE CRUD -----------

# ----------- CATEGORY CRUD -----------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(CategorySerializer(category).data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=204)


# ----------- QUESTIONNAIRE CRUD -----------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def questionnaire_list_create(request):
    if request.method == 'GET':
        gender = request.GET.get("gender")
        category_id = request.GET.get("category")

        filters = {}
        if gender:
            filters["customer_gender"] = gender
        if category_id:
            filters["category_id"] = category_id

        questions = Questionnaire.objects.filter(**filters)
        return Response(QuestionnaireSerializerWithOptions(questions, many=True).data)

    serializer = QuestionnaireSerializerWithOptions(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def questionnaire_detail(request, pk):
    try:
        question = Questionnaire.objects.get(pk=pk)
    except Questionnaire.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(QuestionnaireSerializerWithOptions(question).data)

    elif request.method == 'PUT':
        serializer = QuestionnaireSerializerWithOptions(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        question.delete()
        return Response(status=204)


# ----------- OPTIONS CRUD -----------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def option_list_create(request):
    if request.method == 'GET':
        options = Options.objects.all()
        return Response(OptionsSerializer(options, many=True).data)

    serializer = OptionsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def option_detail(request, pk):
    try:
        option = Options.objects.get(pk=pk)
    except Options.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(OptionsSerializer(option).data)

    elif request.method == 'PUT':
        serializer = OptionsSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        option.delete()
        return Response(status=204)












# ----------- GENERAL PAYMENT RULES -----------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def general_payment_rule_list_create(request):
    if request.method == 'GET':
        doctor_id = request.GET.get('doctor_id')
        search_term = request.GET.get('search')

        rules = GeneralPaymentRules.objects.all()

        if doctor_id:
            try:
                doctor = DoctorProfiles.objects.get(pk=doctor_id)
            except DoctorProfiles.DoesNotExist:
                return Response({"error": "Doctor not found."}, status=404)

            specialization_ids = doctor.doctor_specializations.values_list('specialization_id', flat=True)

            rules = rules.filter(
                specialization_id__in=specialization_ids,
                experience=doctor.experience,
                doctor_flag=doctor.doctor_flag,
              )

        if search_term:
            rules = rules.filter(pricing_name__icontains=search_term)

        serializer = GeneralPaymentRuleSerializer(rules, many=True)
        return Response(serializer.data)

    # POST for new rule creation
    serializer = GeneralPaymentRuleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

from collections import defaultdict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

# @permission_classes([IsAuthenticated, IsAdminUser])
# @api_view(['GET', 'POST'])
# def general_payment_rule_list_create_2(request):
#     if request.method == 'GET':
#         doctor_id = request.GET.get('doctor_id')
#         search_term = request.GET.get('search')

#         rules = GeneralPaymentRules.objects.select_related('country', 'specialization').all()

#         # Filter by doctor if provided
#         if doctor_id:
#             try:
#                 doctor = DoctorProfiles.objects.get(pk=doctor_id)
#             except DoctorProfiles.DoesNotExist:
#                 return Response({"error": "Doctor not found."}, status=404)

#             specialization_ids = doctor.doctor_specializations.values_list('specialization_id', flat=True)

#             rules = rules.filter(
#                 specialization_id__in=specialization_ids,
#                 experience=doctor.experience,
#                 doctor_flag=doctor.doctor_flag,
#             )

#         # Filter by search if provided
#         if search_term:
#             rules = rules.filter(pricing_name__icontains=search_term)

#         # Serialize and group by specialization
#         serializer = GeneralPaymentRuleSerializer(rules, many=True)
#         grouped_rules = defaultdict(list)

#         for item in serializer.data:
#             specialization_name = item['specialization_name']
#             grouped_rules[specialization_name].append(item)

#         return Response(grouped_rules)

#     # --- POST: Create a new rule ---
#     serializer = GeneralPaymentRuleSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=201)

#     return Response(serializer.errors, status=400)


from .serializers import CountryPaymentRuleSerializer


# @permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['GET'])
def general_payment_rule_list_create_2(request):
    doctor_id = request.GET.get('doctor_id')
    search_term = request.GET.get('search')

    rules = GeneralPaymentRules.objects.select_related(
        "specialization", "country"
    )

    # Filter by doctor
    if doctor_id:
        try:
            doctor = DoctorProfiles.objects.get(id=doctor_id)
        except DoctorProfiles.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=404)

        specialization_ids = doctor.doctor_specializations.values_list(
            "specialization_id", flat=True
        )

        rules = rules.filter(
            specialization_id__in=specialization_ids,
            experience=doctor.experience,
            doctor_flag=doctor.doctor_flag,
        )

    # Search filter
    if search_term:
        rules = rules.filter(pricing_name__icontains=search_term)

    # --- GROUPING LOGIC STARTS HERE ---

    grouped = {}

    for rule in rules:
        spec_id = rule.specialization.specialization_id

        if spec_id not in grouped:
            grouped[spec_id] = {
                "specialization_id": spec_id,
                "specialization_name": rule.specialization.specialization,
                "payment_rules": {}
            }

        country_id = rule.country.id

        if country_id not in grouped[spec_id]["payment_rules"]:
            grouped[spec_id]["payment_rules"][country_id] = {
                "country_id": country_id,
                "country_name": rule.country.country_name,
                "currency_symbol": rule.country.currency_symbol,
                "rules": []
            }

        grouped[spec_id]["payment_rules"][country_id]["rules"].append(rule)

    # Convert dict → list + serialize
    final_data = []

    for spec_id, spec_data in grouped.items():
        country_blocks = list(spec_data["payment_rules"].values())
        spec_data["payment_rules"] = CountryPaymentRuleSerializer(country_blocks, many=True).data
        final_data.append(spec_data)

    return Response(final_data)




@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def general_payment_rule_detail(request, pk):
    try:
        rule = GeneralPaymentRules.objects.get(pk=pk)
    except GeneralPaymentRules.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(GeneralPaymentRuleSerializer(rule).data)

    elif request.method == 'PUT':
        serializer = GeneralPaymentRuleSerializer(rule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        rule.delete()
        return Response(status=204)


# ----------- DOCTOR PAYMENT ASSIGNMENTS -----------


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
    










class DoctorProfileUpdateView(generics.UpdateAPIView):
    queryset = DoctorProfiles.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'doctor_profile_id'


from customer.models import CustomerProfile
from .serializers import CustomerProfileSerializer,AppointmentSerializer
from django.db.models import Q

class Patient_List_View(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        search_query = request.GET.get('search', '')
        
        patients = CustomerProfile.objects.all()
        
        if search_query:
            patients = patients.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query)
            )
            serializer = CustomerProfileSerializer(patients, many=True)
            return Response(serializer.data)
        else:
            serializer = CustomerProfileSerializer(patients, many=True)
            return Response(serializer.data)



class Customer_Appointments_View(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        cid = request.GET.get('cid')
        try:
            appointments = AppointmentHeader.objects.filter(customer=CustomerProfile.objects.get(id=cid))
        except CustomerProfile.DoesNotExist:
            return Response("Customer not found",status=404)
        except AppointmentHeader.DoesNotExist:
            return Response("No appointments found",status=404)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)    
    