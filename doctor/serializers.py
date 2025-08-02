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
        fields = ['specialization']
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
    referred_by = serializers.CharField(source="doctor.user.username", default=None)
    referred_to = serializers.CharField(source="referred_doctor.user.username", default=None)

    class Meta:
        model = Referral
        fields = ['referred_by', 'referred_to', 'referred_date', 'referral_notes']


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
            'username', 'first_name', 'last_name', 'preferred_name', 'gender', 'age',
            'weight', 'height','height_unit','weight_unit', 'mobile_number', 'address', 'profile_pic', 'date_of_birth'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.first_name', default=None)
    specialization = serializers.CharField(source='specialization.specialization', default=None)
    category = serializers.CharField(source='category.title', default=None)

    class Meta:
        model = AppointmentHeader
        fields = [
            'appointment_id', 'appointment_date', 'appointment_time', 'start_time',
            'end_time', 'appointment_status', 'doctor_name', 'specialization', 'category',
            'language_pref', 'gender_pref', 'meeting_link', 'payment_done', 
            'prescription', 'appointment_notes','language_pref','gender_pref'
        ]





class ExtraQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra_questions
        fields = ['id', 'question']


class Observation_notes_serializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()

    class Meta:
        model = Observation_Notes
        fields = ['id' , 'note' , 'doctor' , 'date' ]
    
    def get_doctor(self, obj):
        first = obj.appointment.doctor.first_name
        last = obj.appointment.doctor.last_name
        return f"{first} {last}".strip()
    



class PrescribedMedicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescribed_Medications
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrescribedTestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescribed_Tests
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
