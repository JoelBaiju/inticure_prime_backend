from rest_framework import serializers

from analysis.models import Category,Questionnaire,Options,AnswerType,AppointmentHeader
from general.models import Invoices
from general.utils import convert_utc_to_local_return_dt

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(allow_null=True,required=False)
    class Meta:
        model = Category
        fields = "__all__"

class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields="__all__"


class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = "__all__"


class QuestionnaireSerializerWithOptions(serializers.ModelSerializer):
    options = OptionsSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = ['id', 'question', 'answer_type', 'category', 'customer_gender', 'options']

        
class InvoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Invoices
        fields="__all__"
class AnswerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=AnswerType
        fields="__all__"
        
class AppointmentHeaderSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_dob = serializers.SerializerMethodField()
    customer_confirmation_contact_detail = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_language = serializers.SerializerMethodField()
    doctor_gender = serializers.SerializerMethodField()
    specialization = serializers.CharField(source='.specialization_name', read_only=True)
    appointment_time = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentHeader
        fields = [  "appointment_id","customer_name" , "customer_message"  ,
                    "customer_dob" , "customer_confirmation_contact_detail" ,
                    "appointment_id", "start_time", "end_time", "appointment_time",
                    "doctor_name","doctor_language","doctor_gender","meeting_link",'specialization',
                    "appointment_date"
                ]

    def get_appointment_date(self, obj):
        if obj.start_time:
            return convert_utc_to_local_return_dt( obj.start_time , obj.customer.time_zone).date()
        return "Date not specified"

    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.user.first_name} {obj.customer.user.last_name}"
        return "Unknown Customer"
    def get_appointment_time(self, obj):
        if obj.start_time :
            return convert_utc_to_local_return_dt(obj.start_time , obj.customer.time_zone).time()
        return "Time not specified"
    
    def get_customer_dob(self, obj):
        if obj.customer:    
            return obj.customer.date_of_birth
        return None
    
    def get_customer_confirmation_contact_detail(self, obj):
        if obj.customer.confirmation_method == 'whatsapp':
            return obj.customer.whatsapp_number 
        elif obj.customer.confirmation_method == 'email':
            return obj.customer.email
        return None
    def get_doctor_name(self, obj):
        if obj.doctor:
            return f"{obj.doctor.first_name} {obj.doctor.last_name}"
        return "Unknown Doctor"
    def get_doctor_language(self, obj):
        if obj.doctor and obj.doctor.known_languages.exists():
            languages = obj.doctor.known_languages.all()
            known_languages = ", ".join([lang.language.language for lang in languages if lang.language])
            return known_languages
        return "Not Specified"
    def get_doctor_gender(self, obj):
        if obj.doctor:
            return obj.doctor.gender
        return "Not Specified"
    


from rest_framework import serializers
from doctor.models import DoctorProfiles, DoctorLanguages, DoctorSpecializations


class DoctorLanguageSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source='language.language')

    class Meta:
        model = DoctorLanguages
        fields = ['language']


class DoctorSpecializationSerializer(serializers.ModelSerializer):
    specialization = serializers.CharField(source='specialization.specialization')

    class Meta:
        model = DoctorSpecializations
        fields = ['specialization', 'time_duration']


class DoctorProfilePublicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    languages = DoctorLanguageSerializer(many=True, source='known_languages')
    specializations = DoctorSpecializationSerializer(many=True, source='doctor_specializations')

    class Meta:
        model = DoctorProfiles
        fields = ['doctor_profile_id','name', 'doctor_bio', 'profile_pic', 'languages', 'specializations','qualification','is_prescription_allowed']

    def get_name(self, obj):
        return f"{obj.salutation} {obj.first_name} "






