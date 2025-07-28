from rest_framework import serializers
from .models import  DoctorLanguages,DoctorProfiles

class DoctorLanguagesSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source='language.language', read_only=True)
    class Meta:
        model = DoctorLanguages
        fields = ['language']








from rest_framework import serializers
from .models import DoctorProfiles, DoctorSpecializations
from django.contrib.auth.models import User
from administrator.models import Specializations
from analysis.models import AppointmentHeader




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
    





from rest_framework import serializers
from .models import GeneralTimeSlots

class GeneralTimeSlotSerializer(serializers.ModelSerializer):
    slot_time = serializers.SerializerMethodField()
    slot_date = serializers.DateField(source='date.date')

    class Meta:
        model = GeneralTimeSlots
        fields = ['id', 'slot_date', 'slot_time']

    def get_slot_time(self, obj):
        return f"{obj.from_time.strftime('%H:%M')} - {obj.to_time.strftime('%H:%M')}"




# serializers.py

from rest_framework import serializers

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




from analysis.models import Referral

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