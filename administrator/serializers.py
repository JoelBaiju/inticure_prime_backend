

from datetime import timedelta

from rest_framework import serializers
from .models import *
from doctor.models import DoctorProfiles 


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = ['id','country_name', 'country_code', 'currency', 'representation' , 'currency_symbol']



class LanguagesKnownSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguagesKnown
        fields = ['id', 'language']


class SpecializationsSerializer(serializers.ModelSerializer):
    is_couple = serializers.SerializerMethodField()
    class Meta:
        model = Specializations
        fields = ['specialization_id', 'specialization' , 'is_couple' ]

    def get_is_couple(self, obj):
        if  obj.double_session_duration and obj.double_session_duration >timedelta(seconds=0):
            return True
        else:
            return False
        

class SpecializationsSerializerFull(serializers.ModelSerializer):
    double_session_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Specializations
        fields = ['specialization_id', 'specialization', 'description', 'double_session_duration', 'single_session_duration','is_prescription_allowed']


    def get_double_session_duration(self, obj):
        if not obj.double_session_duration:
            return None

        total_seconds = int(obj.double_session_duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"


class SpecializationsSerializerWrite(serializers.ModelSerializer):
    
    class Meta:
        model = Specializations
        fields = "__all__"


from doctor.models import DoctorSpecializations
class DoctorProfileSerializer(serializers.ModelSerializer):
    specializations = serializers.SerializerMethodField()
    country = serializers.StringRelatedField()
    profile_pic=serializers.FileField()
    known_languages = serializers.SerializerMethodField()
    certificate_file = serializers.FileField()
    sign_file_name = serializers.FileField()
    address_proof = serializers.FileField()
    status = serializers.SerializerMethodField()
    doctor_payment_rates = serializers.SerializerMethodField()
    payment_rate_added = serializers.SerializerMethodField()
    class Meta:
        model = DoctorProfiles
        fields = [
            "doctor_profile_id",
            "first_name",
            "last_name",
            "mobile_number",
            "email_id",
            "gender",
            "qualification",
            "registration_year",
            "joined_date",
            "accepted_date",
            "specializations",
            "doctor_flag",
            "experience",
            "doctor_flag",
            "country",
            "profile_pic",
            "known_languages",
            "address",
            "doctor_bio",
            "certificate_no",
            "certificate_file",
            "address_proof",
            "sign_file_name",
            "status",
            "doctor_payment_rates",
            "payment_rate_added",
            "rejection_reason",
            "salutation",
            "is_prescription_allowed"
        ]

    def get_specializations(self, obj):
        return list(obj.doctor_specializations.values_list('specialization__specialization', flat=True))
    def get_payment_rate_added(self, obj):
        # Get all specializations for this doctor
        doc_specialization_ids = DoctorSpecializations.objects.filter(
            doctor=obj
        ).values_list('specialization_id', flat=True)

        for spec_id in doc_specialization_ids:
            has_valid_rate = DoctorPaymentRules.objects.filter(
                doctor=obj,
                specialization_id=spec_id,
            ).filter(
                models.Q(actual_price_single__isnull=False) |
                models.Q(custom_user_total_fee_single__isnull=False) |
                models.Q(actual_price_couple__isnull=False) |
                models.Q(custom_user_total_fee_couple__isnull=False)
            ).exists()

            if not has_valid_rate:
                return False  # No valid pricing at all for this specialization

        return True  # All specializations have at least one rate


    def get_doctor_payment_rates(self, obj):
        assignments = obj.payment_assignments.select_related(
            'specialization', 'country', 'general_rule'
        ).all()
        return DoctorPaymentRuleSerializer(assignments, many=True).data

    def get_known_languages(self, obj):
        return list(
            obj.known_languages.filter(language__isnull=False).values_list('language__language', flat=True)
        )
    def get_status(self,obj):
        if obj.is_accepted:
            return "accepted"
        elif obj.rejected:
            return "rejected"
        else:
            return "pending"
        








class DoctorProfileSerializer_update(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfiles
        fields = '__all__'
        read_only_fields = ['doctor_profile_id', 'user', 'joined_date']











from .models import GeneralPaymentRules, Countries, Specializations
from rest_framework import serializers
from doctor.models import DoctorProfiles,DoctorPaymentRules


class GeneralPaymentRuleSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.country_name', read_only=True)
    specialization_name = serializers.CharField(source='specialization.specialization', read_only=True)
    experience_display = serializers.CharField(source='get_experience_display', read_only=True)
    doctor_flag_display = serializers.CharField(source='get_doctor_flag_display', read_only=True)
    currency_symbol = serializers.CharField(source='country.currency_symbol', read_only=True)  # Ensure currency is defined in Countries

    class Meta:
        model = GeneralPaymentRules
        fields = [
            'id', 'pricing_name',
            'country', 'country_name',
            'specialization', 'specialization_name',
            'experience', 'experience_display',
            'doctor_flag', 'doctor_flag_display',
            'session_count',
            'doctor_fee_single', 'user_total_fee_single',
            'doctor_fee_couple', 'user_total_fee_couple',
            'actual_price_single', 'actual_price_couple',
            'currency_symbol'
        ]




# class DoctorPaymentRuleSerializer(serializers.ModelSerializer):
#     doctor_name = serializers.SerializerMethodField()
#     specialization_name = serializers.CharField(source='specialization.specialization', read_only=True)
#     country_name = serializers.CharField(source='country.country_name', read_only=True)
#     currency_symbol = serializers.CharField(source='country.currency_symbol', read_only=True)

#     doctor_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
#     doctor_fee_couple = serializers.CharField( required=False, write_only=True)
#     user_total_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
#     user_total_fee_couple = serializers.CharField( required=False, write_only=True)

#     custom_doctor_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
#     custom_user_total_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
#     custom_doctor_fee_couple = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
#     custom_user_total_fee_couple = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
#     doctor_flag = serializers.CharField(source='doctor.doctor_flag', read_only=True)
#     experience = serializers.CharField(source='doctor.experience', read_only=True)
#     effective_payment = serializers.SerializerMethodField()

#     class Meta:
#         model = DoctorPaymentRules
#         fields = [
#             'id', 'pricing_name', 'doctor', 'doctor_name',
#             'specialization', 'specialization_name',
#             'country', 'country_name',
#             'session_count', 'currency_symbol',
#             'general_rule', 
#             'doctor_fee_single', 'doctor_fee_couple',
#             'user_total_fee_single', 'user_total_fee_couple',
#             'actual_price_single', 'actual_price_couple',
#             'custom_doctor_fee_single','custom_user_total_fee_single',
#             'custom_doctor_fee_couple', 'custom_user_total_fee_couple',
#             'effective_payment','doctor_flag', 'experience'
#         ]


#     def get_doctor_name(self, obj):
#         return f"{obj.doctor.first_name} {obj.doctor.last_name}" if obj.doctor else None

#     def create(self, validated_data):
#         print("Step 1: Initial validated_data:", validated_data)
#         alias_map = {
#             'custom_doctor_fee_single': validated_data.pop('doctor_fee_single', None),
#             'custom_doctor_fee_couple': validated_data.pop('doctor_fee_couple', 0),
#             'custom_user_total_fee_single': validated_data.pop('user_total_fee_single', None),
#             'custom_user_total_fee_couple': validated_data.pop('user_total_fee_couple', 0),
#         }
#         doctor_fee_single = validated_data.get("doctor_fee_single")
#         if doctor_fee_single not in [None, ""]:
#             try:
#                 validated_data["doctor_fee_single"] = float(doctor_fee_single)
#             except ValueError:
#                 validated_data["doctor_fee_single"] = None  # or raise error
#         print("Step 2: alias_map after pop:", alias_map)
#         validated_data.update({k: v for k, v in alias_map.items() if v is not None})
#         print("Step 3: validated_data after alias_map update:", validated_data)

#         general_rule = validated_data.get('general_rule')
#         print("Step 4: general_rule:", general_rule)
        
#         if isinstance(general_rule, int) or not isinstance(general_rule, GeneralPaymentRules):
#             general_rule = GeneralPaymentRules.objects.select_related('specialization', 'country').filter(
#                 id=general_rule.id if hasattr(general_rule, 'id') else general_rule
#             ).first()
#             validated_data['general_rule'] = general_rule

       
#         if general_rule is not None:
#             print("general_rule.specialization:", general_rule.specialization)
#             print("general_rule.country:", general_rule.country)
#             validated_data['specialization'] = general_rule.specialization
#             validated_data['country'] = general_rule.country
#             validated_data['pricing_name'] = general_rule.pricing_name or ''
#             validated_data['session_count'] = general_rule.session_count
#             validated_data['actual_price_single'] = general_rule.actual_price_single
#             validated_data['actual_price_couple'] = general_rule.actual_price_couple
#             print("Step 5: validated_data after setting from general_rule:", validated_data)

#         # Move this check AFTER general_rule fields are set
#         required_fields = ['specialization', 'country', 'session_count']
#         for field in required_fields:
#             print(f"Step 6: Checking required field '{field}':", validated_data.get(field))
#             if not validated_data.get(field):
#                 print(f"Step 6.1: Missing required field '{field}'")
#                 raise serializers.ValidationError({field: ['This field is required.']})

#         print("Step 7: Checking for duplicate DoctorPaymentAssignments")
#         if DoctorPaymentRules.objects.filter(
#             doctor=validated_data['doctor'],
#             specialization=validated_data['specialization'],
#             country=validated_data['country'],
#             session_count=validated_data['session_count']
#         ).exists():
#             print("Step 7.1: Duplicate assignment found")
#             raise serializers.ValidationError("Duplicate assignment for this doctor and rule combination.")

#         print("Step 8: Calling super().create with validated_data:", validated_data)
#         return super().create(validated_data)



#     def get_effective_payment(self, obj):
#         return obj.get_effective_payment() or {}



from decimal import Decimal, InvalidOperation

class DoctorPaymentRuleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    specialization_name = serializers.CharField(source='specialization.specialization', read_only=True)
    country_name = serializers.CharField(source='country.country_name', read_only=True)
    currency_symbol = serializers.CharField(source='country.currency_symbol', read_only=True)

    # Accept as strings, but we’ll sanitize later
    doctor_fee_single = serializers.CharField(required=False, allow_blank=True, write_only=True)
    doctor_fee_couple = serializers.CharField(required=False, allow_blank=True, write_only=True)
    user_total_fee_single = serializers.CharField(required=False, allow_blank=True, write_only=True)
    user_total_fee_couple = serializers.CharField(required=False, allow_blank=True, write_only=True)

    custom_doctor_fee_single = serializers.CharField(required=False, allow_blank=True, write_only=True)
    custom_user_total_fee_single = serializers.CharField(required=False, allow_blank=True, write_only=True)
    custom_doctor_fee_couple = serializers.CharField(required=False, allow_blank=True, write_only=True)
    custom_user_total_fee_couple = serializers.CharField(required=False, allow_blank=True, write_only=True)

    doctor_flag = serializers.CharField(source='doctor.doctor_flag', read_only=True)
    experience = serializers.CharField(source='doctor.experience', read_only=True)
    effective_payment = serializers.SerializerMethodField()

    class Meta:
        model = DoctorPaymentRules
        fields = [
            'id', 'pricing_name', 'doctor', 'doctor_name',
            'specialization', 'specialization_name',
            'country', 'country_name',
            'session_count', 'currency_symbol',
            'general_rule', 
            'doctor_fee_single', 'doctor_fee_couple',
            'user_total_fee_single', 'user_total_fee_couple',
            'actual_price_single', 'actual_price_couple',
            'custom_doctor_fee_single','custom_user_total_fee_single',
            'custom_doctor_fee_couple', 'custom_user_total_fee_couple',
            'effective_payment','doctor_flag', 'experience'
        ]

    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}" if obj.doctor else None

    def _safe_decimal(self, value):
        """Convert string/float to Decimal safely."""
        if value in [None, ""]:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    def create(self, validated_data):
        print("Step 1: Initial validated_data:", validated_data)

        alias_map = {
            'custom_doctor_fee_single': validated_data.pop('doctor_fee_single', None),
            'custom_doctor_fee_couple': validated_data.pop('doctor_fee_couple', None),
            'custom_user_total_fee_single': validated_data.pop('user_total_fee_single', None),
            'custom_user_total_fee_couple': validated_data.pop('user_total_fee_couple', None),
        }

        # Convert all fee-related fields to Decimal or None
        for k, v in alias_map.items():
            alias_map[k] = self._safe_decimal(v)

        print("Step 2: alias_map after conversion:", alias_map)
        validated_data.update({k: v for k, v in alias_map.items() if v is not None})
        print("Step 3: validated_data after alias_map update:", validated_data)

        general_rule = validated_data.get('general_rule')
        print("Step 4: general_rule:", general_rule)

        if isinstance(general_rule, int) or not isinstance(general_rule, GeneralPaymentRules):
            general_rule = GeneralPaymentRules.objects.select_related('specialization', 'country').filter(
                id=general_rule.id if hasattr(general_rule, 'id') else general_rule
            ).first()
            validated_data['general_rule'] = general_rule

        if general_rule is not None:
            validated_data['specialization'] = general_rule.specialization
            validated_data['country'] = general_rule.country
            validated_data['pricing_name'] = general_rule.pricing_name or ''
            validated_data['session_count'] = general_rule.session_count
            validated_data['actual_price_single'] = general_rule.actual_price_single
            validated_data['actual_price_couple'] = general_rule.actual_price_couple
            print("Step 5: validated_data after setting from general_rule:", validated_data)

        required_fields = ['specialization', 'country', 'session_count']
        for field in required_fields:
            if not validated_data.get(field):
                raise serializers.ValidationError({field: ['This field is required.']})

        if DoctorPaymentRules.objects.filter(
            doctor=validated_data['doctor'],
            specialization=validated_data['specialization'],
            country=validated_data['country'],
            session_count=validated_data['session_count']
        ).exists():
            raise serializers.ValidationError("Duplicate assignment for this doctor and rule combination.")

        return super().create(validated_data)

    def get_effective_payment(self, obj):
        return obj.get_effective_payment() or {}















from rest_framework import serializers
from customer.models import CustomerProfile, Customer_Package
from analysis.models import Prescribed_Medications
from doctor.models import DoctorProfiles
from django.contrib.auth.models import User


# Serializer for prescribed medications
class PrescribedMedicationsSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Prescribed_Medications
        fields = [
            'medicine_name', 'dosage', 'strength', 'frequency', 'duration', 
            'instruction', 'is_active', 'created_at', 'doctor_name'
        ]

# Serializer for the customer's package history
class CustomerPackageSerializer(serializers.ModelSerializer):
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Customer_Package
        fields = [
            'package_name', 'is_active', 'appointments_got', 'appointments_left',
            'is_couple', 'expires_on', 'specialization_name', 'doctor_name'
        ]


# Main CustomerProfileSerializer with nested data
class CustomerProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    customer_package = CustomerPackageSerializer(many=True, read_only=True)
    prescribed_medications = PrescribedMedicationsSerializer(many=True, read_only=True)
    country_details = serializers.CharField(source='country_details.country_name', read_only=True)
    confirmation_method = serializers.SerializerMethodField

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_confirmation_method(self, obj):
        print(obj.confirmation_method)
        print(obj.confirmation_method in ["Both", "both"])
        return "WhatsApp and Email" if obj.confirmation_method in ["Both", "both"] else obj.confirmation_method

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'name', 'user', 'partner', 'gender', 'other_gender', 'address',
            'date_of_birth', 'mobile_number', 'email', 'whatsapp_number', 
            'country_details', 'height_unit', 'profile_pic', 'completed_first_analysis',
            'preferred_name', 'weight', 'weight_unit', 'height', 'time_zone', 
            'confirmation_method', 'customer_package', 'prescribed_medications'
        ]






class CustomerProfileSerializerFull(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'





































from rest_framework import serializers
from analysis.models import (
    AppointmentHeader, Observation_Notes, Follow_Up_Notes, 
    Prescribed_Medications, Prescribed_Tests, Notes_for_patient,
)
from customer.models import CustomerProfile,AppointmentRatings
from doctor.models import DoctorProfiles
from administrator.models import Specializations
from django.contrib.auth.models import User
from general.utils import convert_utc_to_local_return_dt

# We need these nested serializers
class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class DoctorProfileNestedSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    class Meta:
        model = DoctorProfiles
        fields = ['id', 'user']

class ObservationNotesSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.preferred_name', read_only=True)
    class Meta:
        model = Observation_Notes
        fields = ['note', 'date', 'customer_name']

class FollowUpNotesSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.preferred_name', read_only=True)
    class Meta:
        model = Follow_Up_Notes
        fields = ['note', 'date', 'customer_name']

class PrescribedMedicationsSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    class Meta:
        model = Prescribed_Medications
        fields = [
            'medicine_name', 'dosage', 'strength', 'frequency', 
            'duration', 'instruction', 'is_active', 'doctor_name'
        ]

class PrescribedTestsSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    class Meta:
        model = Prescribed_Tests
        fields = ['test_name', 'instruction', 'submitted', 'doctor_name']

class AppointmentRatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentRatings
        fields = ['rating', 'rating_comments', 'added_by']

# Main Appointment Serializer
class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_id = serializers.SerializerMethodField()
    specialization_name = serializers.CharField(source='specialization.specialization', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True) # Added field
    customer_details = serializers.SerializerMethodField()
    partner_details = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    type_booking = serializers.SerializerMethodField()
    reschedule_details = serializers.SerializerMethodField()
    
    # New nested fields
    observation_notes = ObservationNotesSerializer(many=True, read_only=True)
    follow_up_notes = FollowUpNotesSerializer(many=True, read_only=True)
    prescribed_medications = PrescribedMedicationsSerializer(many=True, read_only=True)
    prescribed_tests = PrescribedTestsSerializer(many=True, read_only=True)
    ratings = AppointmentRatingsSerializer(many=True, read_only=True, source='appointmentratings_set')

    class Meta:
        model = AppointmentHeader
        fields = [
            'appointment_id', 'doctor_name', 'doctor_id', 'specialization_name',
            'category_title', # Added field
            'customer_details', 'partner_details', 'appointment_time', 
            'appointment_date', 'appointment_status', 'type_booking',
            'meeting_link', 'booked_by', 'is_couple', 'completed',
            'file_is_open', 'followup', 'package_included', 'package_used',
            'reschedule_details', 'customer_message', # Added fields
            'observation_notes', 'follow_up_notes', 'prescribed_medications',
            'prescribed_tests', 'ratings'
        ]

    def get_doctor_name(self, obj):
        if obj.doctor:
            return f"{obj.doctor.first_name} {obj.doctor.last_name}"
        return None

    def get_doctor_id(self, obj):
        if obj.doctor:
            return obj.doctor.doctor_profile_id
        return None

    def get_customer_details(self, obj):
        customer = obj.customer
        if not customer:
            return None
        
        return {
            'id': customer.id,
            'name': f"{customer.user.first_name} {customer.user.last_name}",
            'email': customer.email,
            'mobile': customer.whatsapp_number,
            'time_zone': customer.time_zone
        }

    def get_partner_details(self, obj):
        if not obj.is_couple or not obj.partner_customer:
            return None
        
        partner = obj.partner_customer
        return {
            'name': f"{partner.user.first_name} {partner.user.last_name}",
            'email': partner.email,
            'mobile': partner.whatsapp_number
        }

    def get_appointment_time(self, obj):
        if not obj.start_time:
            return None
        return convert_utc_to_local_return_dt(obj.start_time, "Asia/Calcutta").time()

    def get_appointment_date(self, obj):
        if not obj.start_time:
            return None
        return convert_utc_to_local_return_dt(obj.start_time, "Asia/Calcutta").date()

    def get_type_booking(self, obj):
        return "Couples" if obj.is_couple else "Individual"

    def get_reschedule_details(self, obj):
        latest_reschedule = obj.reschedule_history.order_by('-initiated_on').first()
        if not latest_reschedule:
            return None
        
        return {
            'rescheduled_on': convert_utc_to_local_return_dt(latest_reschedule.initiated_on, "Asia/Calcutta"),
            'rescheduled_by': latest_reschedule.initiated_by,
            'reschedule_reason': latest_reschedule.reason
        }



from customer.models import Refund
from doctor.models import Payouts

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'

class PayoutsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payouts
        fields = '__all__'
