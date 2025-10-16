from django.contrib.auth.models import User
from customer.models import CustomerProfile
from administrator.models import Countries


class ProfileService:
    """Service class for managing customer profiles and related operations"""
    
    @staticmethod
    def get_profile(user_id):
        """Get customer profile by user ID"""
        try:
            return CustomerProfile.objects.get(user_id=user_id)
        except CustomerProfile.DoesNotExist:
            return None
            
    @staticmethod
    def create_profile(user_data):
        """Create a new customer profile"""
        try:
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password=user_data['password']
            )
            
            country = Countries.objects.get(id=user_data['country_id'])
            
            profile = CustomerProfile.objects.create(
                user=user,
                email=user_data['email'],
                mobile_number=user_data['phone_number'],
                country_details=country,
                whatsapp_number=user_data.get('whatsapp_number')
            )
            return profile
        except Exception as e:
            raise Exception(f"Error creating profile: {str(e)}")
            
    @staticmethod
    def update_profile(user_id, update_data):
        """Update existing customer profile"""
        try:
            profile = CustomerProfile.objects.get(user_id=user_id)
            
            if 'email' in update_data:
                profile.email = update_data['email']
            if 'phone_number' in update_data:
                profile.mobile_number = update_data['phone_number']
            if 'country_id' in update_data:
                profile.country_details = Countries.objects.get(id=update_data['country_id'])
            if 'whatsapp_number' in update_data:
                profile.whatsapp_number = update_data['whatsapp_number']
                
            profile.save()
            return profile
        except CustomerProfile.DoesNotExist:
            raise Exception("Profile not found")
        except Exception as e:
            raise Exception(f"Error updating profile: {str(e)}")
            
    @staticmethod 
    def delete_profile(user_id):
        """Delete customer profile and associated user"""
        try:
            profile = CustomerProfile.objects.get(user_id=user_id)
            user = profile.user
            profile.delete()
            user.delete()
            return True
        except CustomerProfile.DoesNotExist:
            raise Exception("Profile not found")
        except Exception as e:
            raise Exception(f"Error deleting profile: {str(e)}")
    @staticmethod
    def get_customer_contact_details(user):
        """Get customer contact details"""
        customer_profile = CustomerProfile.objects.get(user=user)
        return {
            "email": customer_profile.email,
            "phone_number": customer_profile.mobile_number,
            "country_code": customer_profile.country_details.country_code if customer_profile.country_details else None,
            "whatsapp_number": customer_profile.whatsapp_number,
        }

    @staticmethod
    def create_partner_profile(partner_data):
        """Create a partner profile for existing customer"""
        # try:
        country = Countries.objects.get(id=partner_data['country_id'])
        user = User.objects.create_user(
            username=partner_data['email'],
            email=partner_data['email'] if partner_data['email'] else partner_data['phone_number'],
            password=partner_data['email'] if partner_data['email'] else " " +partner_data['phone_number'] if partner_data['phone_number'] else " ",
            first_name=partner_data['first_name'],
            last_name=partner_data['last_name'],
        )
        profile = CustomerProfile.objects.create(
            user=user,
            email=partner_data['email'],
            mobile_number=partner_data['phone_number'],
            country_details=country,
            whatsapp_number=partner_data['whatsapp_number'],
            gender=partner_data['gender'],
            date_of_birth=partner_data['dob'],  
            country_code=partner_data['country_code'],
            mob_country_code=partner_data['mob_country_code'],
            partner_id=partner_data['partners_id'] if partner_data['partners_id'] not in [0,'0',None,""," "] else None,
            confirmation_method = "email" if partner_data['email'] else "phone",
            completed_first_analysis = True
        )

        if partner_data['partners_id'] not in [0,'0',None,""," "]:
            print(partner_data["partners_id"])
            customer = CustomerProfile.objects.get(id=partner_data['partners_id'])
            customer.partner = profile
            customer.save()
        return profile
        # except Exception as e:
        #     raise Exception(f"Error creating partner profile: {str(e)}")