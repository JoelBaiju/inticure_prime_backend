from rest_framework import serializers
from analysis.models import *
from .models import *
from customer.models import *
from collections import defaultdict





class DoctorLanguagesSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source='language.language', read_only=True)
    class Meta:
        model = DoctorLanguages
        fields = ['language']



class DoctorProfileCreateSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = DoctorProfiles
        fields = "__all__"



class DoctorProfileSerializer_Dashboard(serializers.ModelSerializer):
    specializations = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfiles
        fields = ["first_name", "last_name", "specializations", "registration_year"]

    def get_specializations(self, obj): 
        return list(obj.doctor_specializations.values_list('specialization__specialization', flat=True))


class AppointmentsSerializer_For_Doctor_Dashboard(serializers.ModelSerializer):
    
    class Meta:
        model = AppointmentHeader
        fields =[""]
    

from general.models import CommonFileUploader
class CommonFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonFileUploader
        fields = ['id', 'common_file', 'file_name' ,'uploaded_on' ,'appointment']

class DoctorAvailableHoursSerializer(serializers.Serializer):
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data





class UpcomingAppointmentSerializer(serializers.Serializer):
    specialization = serializers.CharField(source = 'specialization.specialization', read_only=True)
    customer_name = serializers.CharField(source='appointment.customer.user.get_full_name', read_only=True)

    class Meta:
        fields = ['appointment_id', 'appointment_date', 'appointment_time', 'specialization','customer_name']





class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'
        read_only_fields = ['referred_date']  # auto_now_add, so don't allow input



class doctorSpecializationSerializer(serializers.ModelSerializer):
    specialization = serializers.CharField(source='specialization.specialization', read_only=True)
    
    class Meta:
        model = DoctorSpecializations
        fields = ['specialization','specialization_id']
        read_only_fields = ['specialization']  # Ensure this field is read-only





class GroupedQuestionAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answers = serializers.ListField(child=serializers.CharField())

    @classmethod
    def from_queryset(cls, queryset):
        grouped = defaultdict(list)

        for obj in queryset:
            question_text = obj.question.question
            answer_text = obj.answer.option
            grouped[question_text].append(answer_text)

        # Create structured list of dicts
        structured_data = [
            {"question": question, "answers": list(set(answers))}
            for question, answers in grouped.items()
        ]

        # Serialize the structured data
        return cls(structured_data, many=True).data


class ExtraQuestionAnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source="question.question", default=None)

    class Meta:
        model = Extra_questions_answers
        fields = ['question', 'answer']



class ReferralSerializer(serializers.ModelSerializer):
    referred_by = serializers.CharField(source="doctor.user.username", default=None,read_only=True)
    referred_to = serializers.CharField(source="referred_doctor.user.username", default=None,read_only=True )

    class Meta:
        model = Referral
        fields = ['referred_by', 'referred_to', 'referred_date', 'referral_notes']


class ReferralSerializerCreate(serializers.ModelSerializer):
    
    class Meta:
        model = Referral
        fields = "__all__"


class SuggestedPlanSerializer(serializers.ModelSerializer):
    plan_title = serializers.CharField(source="plan.__str__", default=None)

    class Meta:
        model = Doctor_Suggested_Plans
        fields = ['plan_id', 'plan_title']


class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.first_name')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = CustomerProfile
        fields = [
            'username', 'first_name', 'last_name', 'preferred_name', 'gender','id',
            'weight', 'height','height_unit','weight_unit', 'mobile_number', 'address', 'profile_pic', 'date_of_birth'
        ]


from general.utils import convert_utc_to_local_return_dt
class AppointmentDetailSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.first_name', default=None)
    specialization = serializers.CharField(source='specialization.specialization', default=None)
    category = serializers.CharField(source='category.title', default=None)
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    doctor_meeting_link = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentHeader
        fields = [
            'appointment_id', 'appointment_status', 'doctor_name', 'specialization', 'category',
            'language_pref', 'gender_pref', 'doctor_meeting_link', 'payment_done', 
            'language_pref','gender_pref','start_time', 'end_time' , 'appointment_date',
            
        ]

    def get_start_time(self, obj):
        return convert_utc_to_local_return_dt(obj.start_time, obj.doctor.time_zone)
    def get_end_time(self, obj):
        return convert_utc_to_local_return_dt(obj.end_time, obj.doctor.time_zone)
    def get_appointment_date(self, obj):
        return convert_utc_to_local_return_dt(obj.start_time, obj.doctor.time_zone).date()
    def get_doctor_meeting_link(self,obj):
        if obj.appointment_status != "confirmed":
            return None
        tracker = Meeting_Tracker.objects.get(appointment = obj)
        return tracker.doctor_meeting_link        




class ExtraQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra_questions
        fields = ['id', 'question']


class ObservationNotesSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    docid = serializers.StringRelatedField(source='doctor.doctor_profile_id', read_only=True)
    class Meta:
        model = Observation_Notes
        fields = ['id' , 'note' , 'doctor' , 'date' , 'docid' ]
    
    def get_doctor(self, obj):
        first = obj.appointment.doctor.first_name
        last = obj.appointment.doctor.last_name
        salutation = obj.appointment.doctor.salutation
        return f"{salutation} {first} {last}".strip()
    

class Followup_notes_serializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()

    class Meta:
        model = Follow_Up_Notes
        fields = ['id' , 'note' , 'doctor' , 'date' ]
    
    def get_doctor(self, obj):
        first = obj.appointment.doctor.first_name
        last = obj.appointment.doctor.last_name
        return f"{first} {last}".strip()
    



class PrescribedMedicationsSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    doctor_id = serializers.SerializerMethodField()
    class Meta:
        model = Prescribed_Medications
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at' , 'doctor' , "doctor_id"]
    def get_doctor(self, obj):
        first = obj.doctor.first_name
        last = obj.doctor.last_name
        return f"{first} {last}".strip()
    
    def get_doctor_id(self,obj):
        return obj.doctor.doctor_profile_id



class PrescribedMedicationsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prescribed_Medications
        fields = '__all__'
 

class PrescribedTestsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prescribed_Tests
        fields = '__all__'


class PrescribedTestsSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()

    class Meta:
        model = Prescribed_Tests
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at' , 'doctor']

    def get_doctor(self, obj):
        first = obj.doctor.first_name
        last = obj.doctor.last_name
        return f"{first} {last}".strip()



class NotesForPatientSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    docid = serializers.StringRelatedField(source='doctor.doctor_profile_id', read_only=True)

    class Meta:
        model = Notes_for_patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at' , 'doctor' , 'docid']
    def get_doctor(self, obj):
        first = obj.doctor.first_name
        last = obj.doctor.last_name
        salutation = obj.doctor.salutation  
        return f"{salutation} {first} {last}".strip()


class PayoutsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payouts
        fields = '__all__'


class DoctorBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor_Bank_Account
        fields = '__all__'




class DoctorPaymentRulesSerializer(serializers.ModelSerializer):
    pricing = serializers.SerializerMethodField()
    country = serializers.CharField(source='country.country_name', default=None)
    specialization = serializers.CharField(source='specialization.specialization', default=None)
    class Meta:
        model = DoctorPaymentRules
        fields = ['id','pricing','session_count','country','specialization']

    def get_pricing(self, obj):
        pricing = obj.get_effective_payment()
        # return {
        #     'single':pricing['custom_user_total_fee_single'],
        #     'couple':pricing['custom_user_total_fee_couple']
        # }
        return pricing