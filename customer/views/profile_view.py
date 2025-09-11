from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.contrib.auth.models import User

from ..models import CustomerProfile
from administrator.models import Countries
from ..services.profile_service import ProfileService
from ..utils.validators import ProfileValidator
from general.emal_service import send_email_verification_otp_email
from general.models import Email_OTPs ,Phone_OTPs

class ContactDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get customer contact details"""
        try:
            contact_details = ProfileService.get_customer_contact_details(request.user)
            return Response(contact_details, status=status.HTTP_200_OK)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )


class PartnerExistenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Check if a partner exists for the logged-in user"""
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            partner_exists = customer_profile.partner is not None
            return Response(
                {"partner_exists": partner_exists}, 
                status=status.HTTP_200_OK
            )
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )


# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_partner(request):
    """Create a partner profile for existing customer"""
    partner_data = {
        'first_name': request.data.get('first_name'),
        'last_name': request.data.get('last_name'),
        'email': request.data.get('email'),
        'phone_number': request.data.get('phone_number'),
        'gender': request.data.get('gender'),
        'dob': request.data.get('dob'),
        'address': request.data.get('address'),
        'country': request.data.get('country'),
        'preferred_name': request.data.get('preferred_name'),
        'partners_id': request.data.get('partners_id'),
        'whatsapp_number': request.data.get('whatsapp_number'),
        "country_code":request.data.get('country_code'),
        "mob_country_code":request.data.get('mob_country_code')
    }
    print(partner_data)
    
    # try:
        # Validate required fields
    country = Countries.objects.get(country_name = 'India')
    partner_data['country']=country.id
    partner_data['country_id']=country.id
    print(partner_data)
    required_fields = ['first_name', 'last_name', 'country', 'gender', 'dob']
    ProfileValidator.validate_required_fields(partner_data, required_fields)
    
    # Get existing partner
    
    # Create partner profile
    partner_profile = ProfileService.create_partner_profile(partner_data)
    
    return Response({
        "message": "Partner created successfully.",
        "customer_id": partner_profile.id,
        "email": partner_data['email'],
        "phone_number": partner_data['phone_number']
    }, status=status.HTTP_201_CREATED)
        
    # except CustomerProfile.DoesNotExist:
    #     return Response(
    #         {"error": "Partner profile not found."}, 
    #         status=status.HTTP_404_NOT_FOUND
    #     )
    # except ValueError as e:
    #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    # except Exception as e:
    #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





from ..serializers import  CustomerProfileSerializer

class CustomerProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return generics.get_object_or_404(self.get_queryset())




class WhatsappNumberOrEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        whatsapp_number = request.data.get('whatsapp_number')
        country_code = request.data.get('country_code')
        email = request.data.get('email')
        print("Phone number:", whatsapp_number)
        print("email",email)
        if whatsapp_number:
            if len(str(whatsapp_number))>5:
                print("Whatsapp number received and got in:", whatsapp_number)
                otp_instance = Phone_OTPs.objects.create(phone=whatsapp_number , otp = '666666')
                # otp_instance = Phone_OTPs.objects.create(phone=whatsapp_number , otp = generate_random_otp())
                # send_otp_sms(otp = otp_instance.otp , to_number=country_code+whatsapp_number)
                print("OTP sent to phone number:", whatsapp_number)
            
        if email:
            otp_instance = Email_OTPs.objects.create(email=email, otp='666666')
            # otp_instance = Email_OTPs.objects.create(email=email, otp=generate_random_otp())
            send_email_verification_otp_email(otp = otp_instance.otp , to_email=email , name = ' User')
            print("OTP sent to email:", email)
        
            
        return Response({
            'message': 'OTP sent successfully',
            'whatsapp':whatsapp_number ,
            'email': email
        }) 

class VerifyWhatsappNumberOrEmailChangeView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        whatsapp_number = request.data.get('whatsapp_number')
        country_code = request.data.get('country_code')
        email = request.data.get('email')
        otp = request.data.get('otp')
        print(whatsapp_number , otp , email)
        if whatsapp_number:
            if Phone_OTPs.objects.filter(phone=whatsapp_number,otp = otp).exists():
                print("OTP verified successfully")
                user_profile = CustomerProfile.objects.get(user=request.user)
                user_profile.whatsapp_number = whatsapp_number
                user_profile.country_code=country_code
                user_profile.save()
                return Response({
                    'message': 'Whatsapp number updated successfully',
                    'whatsapp': whatsapp_number,
                    "country":user_profile.country_details.country_name,
                    'email': email
                    },
                    status=status.HTTP_200_OK   )
            else:
                return Response({
                    'message': 'Invalid OTP',
                    'whatsapp': whatsapp_number,
                    'email': email
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        elif email:
            if Email_OTPs.objects.filter(email=email,otp = otp).exists():
                print("OTP verified successfully")
                user_profile = CustomerProfile.objects.get(user=request.user)
                user_profile.email = email
                user_profile.save()
                return Response({
                    'message': 'Email updated successfully',
                    'whatsapp': whatsapp_number,
                    "country":user_profile.country_details.country_name,
                    'email': email
                    },
                    status=status.HTTP_200_OK   )
            else:
                return Response({
                    'message': 'Invalid OTP',
                    'whatsapp': whatsapp_number,
                    'email': email
                    },
                    status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_customer_country(request):
    country = request.data.get('country')
    try:
        country = Countries.objects.get(country_name = country)
        customer_profile = CustomerProfile.objects.get(user=request.user)
        customer_profile.country_details = country
        customer_profile.save()
        return Response({
            'message': 'Country updated successfully',
            'country': country.country_name
        }, status=status.HTTP_200_OK)
    except Countries.DoesNotExist:
        return Response(
            {"error": "Country not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except CustomerProfile.DoesNotExist:
        return Response(
            {"error": "Customer profile not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )



from ..serializers import CustomerProfileSerializerMini
class PatientDetailsFromPhoneEmailView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        phone = request.data.get('phone')
        email = request.data.get('email')
        if email:
            try:
                customer_profile = CustomerProfile.objects.get(email=email)
                serializer = CustomerProfileSerializerMini(customer_profile)
                return Response(serializer.data)
            except CustomerProfile.DoesNotExist:
                return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
        elif phone:
            try:
                customer_profile = CustomerProfile.objects.get(whatsapp_number=phone)
                serializer = CustomerProfileSerializerMini(customer_profile)
                return Response(serializer.data)
            except CustomerProfile.DoesNotExist:
                return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Phone number or email is required."}, status=status.HTTP_400_BAD_REQUEST)




class ConnectPartnersView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        partner_id = request.data.get('partner_id')
        if partner_id:
            try:
                partner_profile = CustomerProfile.objects.get(id=partner_id)
                current_customer = CustomerProfile.objects.get(user = request.user)
                current_customer.partner = partner_profile
                partner_profile.partner = current_customer
                current_customer.save()
                partner_profile.save()
                return Response({"message": "Partner connected successfully."}, status=status.HTTP_200_OK)
            except CustomerProfile.DoesNotExist:
                return Response({"error": "Partner profile not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Partner ID is required."}, status=status.HTTP_400_BAD_REQUEST)