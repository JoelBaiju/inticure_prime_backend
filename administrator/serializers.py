

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
    class Meta:
        model = Specializations
        fields = ['specialization_id', 'specialization']


class SpecializationsSerializerFull(serializers.ModelSerializer):
    double_session_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Specializations
        fields = ['specialization_id', 'specialization', 'description', 'double_session_duration', 'single_session_duration']

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
            "rejection_reason"
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




class DoctorPaymentRuleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    specialization_name = serializers.CharField(source='specialization.specialization', read_only=True)
    country_name = serializers.CharField(source='country.country_name', read_only=True)
    currency_symbol = serializers.CharField(source='country.currency_symbol', read_only=True)

    doctor_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    doctor_fee_couple = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    user_total_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    user_total_fee_couple = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)

    custom_doctor_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    custom_user_total_fee_single = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    custom_doctor_fee_couple = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
    custom_user_total_fee_couple = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, write_only=True)
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

    def create(self, validated_data):
        print("Step 1: Initial validated_data:", validated_data)
        alias_map = {
            'custom_doctor_fee_single': validated_data.pop('doctor_fee_single', None),
            'custom_doctor_fee_couple': validated_data.pop('doctor_fee_couple', None),
            'custom_user_total_fee_single': validated_data.pop('user_total_fee_single', None),
            'custom_user_total_fee_couple': validated_data.pop('user_total_fee_couple', None),
        }
        print("Step 2: alias_map after pop:", alias_map)
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
            print("general_rule.specialization:", general_rule.specialization)
            print("general_rule.country:", general_rule.country)
            validated_data['specialization'] = general_rule.specialization
            validated_data['country'] = general_rule.country
            validated_data['pricing_name'] = general_rule.pricing_name or ''
            validated_data['session_count'] = general_rule.session_count
            validated_data['actual_price_single'] = general_rule.actual_price_single
            validated_data['actual_price_couple'] = general_rule.actual_price_couple
            print("Step 5: validated_data after setting from general_rule:", validated_data)

        # Move this check AFTER general_rule fields are set
        required_fields = ['specialization', 'country', 'session_count']
        for field in required_fields:
            print(f"Step 6: Checking required field '{field}':", validated_data.get(field))
            if not validated_data.get(field):
                print(f"Step 6.1: Missing required field '{field}'")
                raise serializers.ValidationError({field: ['This field is required.']})

        print("Step 7: Checking for duplicate DoctorPaymentAssignments")
        if DoctorPaymentRules.objects.filter(
            doctor=validated_data['doctor'],
            specialization=validated_data['specialization'],
            country=validated_data['country'],
            session_count=validated_data['session_count']
        ).exists():
            print("Step 7.1: Duplicate assignment found")
            raise serializers.ValidationError("Duplicate assignment for this doctor and rule combination.")

        print("Step 8: Calling super().create with validated_data:", validated_data)
        return super().create(validated_data)



    def get_effective_payment(self, obj):
        return obj.get_effective_payment() or {}

