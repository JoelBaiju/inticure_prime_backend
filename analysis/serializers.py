from rest_framework import serializers

from analysis.models import Category,Questionnaire,Options,AnswerType,AppointmentHeader
from general.models import Invoices
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
    customer_age = serializers.SerializerMethodField()
    customer_dob = serializers.SerializerMethodField()
    customer_confirmation_contact_detail = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_language = serializers.SerializerMethodField()
    doctor_gender = serializers.SerializerMethodField()
    specialization = serializers.CharField(source='.specialization_name', read_only=True)
    class Meta:
        model = AppointmentHeader
        fields = [  "appointment_id","customer_name" , "customer_message" , "customer_age" ,
                    "customer_dob" , "customer_confirmation_contact_detail" ,
                    "appointment_id", "appointment_date", "appointment_time",
                    "doctor_name","doctor_language","doctor_gender","meeting_link",'specialization'
                ]

    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.user.first_name} {obj.customer.user.last_name}"
        return "Unknown Customer"
    def get_customer_age(self, obj):
        if obj.customer :
            return obj.customer.age
        return None
    def get_customer_dob(self, obj):
        if obj.customer:
            return obj.customer.date_of_birth
        return None
    
    def get_customer_confirmation_contact_detail(self, obj):
        if obj.confirmation_phone_number:
            return obj.confirmation_phone_number
        elif obj.confirmation_email:
            return obj.confirmation_email
        return None
    def get_doctor_name(self, obj):
        if obj.doctor:
            return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}"
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
        fields = ['doctor_profile_id','name', 'doctor_bio', 'profile_pic', 'languages', 'specializations','qualification']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"






