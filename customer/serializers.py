# serializers.py
from rest_framework import serializers
from .models import CustomerProfile
from collections import defaultdict
from django.utils import timezone

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        read_only_fields = ['user']  # user will be set from the request
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    

class CustomerDashboardSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    currently_consulting_doctors = serializers.SerializerMethodField()
    upcoming_appointments = serializers.SerializerMethodField()
    previous_appointments = serializers.SerializerMethodField()
    mobile_number = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    country = serializers.CharField(source='country_details.country_name', read_only=True)
    pending_appointments = serializers.SerializerMethodField()
    class Meta:
        model = CustomerProfile
        fields = ['user' , 'age','gender', 'previous_appointments' ,'upcoming_appointments',
                  'first_name', 'last_name', 'email', 'mobile_number', 'completed_first_analysis',
                  'currently_consulting_doctors', 'country', 'preferred_name','pending_appointments']
        
    def get_currently_consulting_doctors(self, obj):
            appointments = obj.appointment_header.filter(file_is_open=True).order_by('-appointment_date', '-appointment_time')
            doctor_appointments = defaultdict(list)
            for appointment in appointments:
                doctor = appointment.doctor
                doctor_appointments[doctor].append(appointment)

            result = []
            for doctor, appts in doctor_appointments.items():
                last_appointment = sorted(appts, key=lambda x: (x.appointment_date, x.appointment_time), reverse=True)[0]
                result.append({
                    'doctor_id': doctor.doctor_profile_id,
                    'doctor_name': doctor.first_name + ' ' + doctor.last_name,
                    'last_appointment_date': last_appointment.appointment_date,
                    'last_appointment_time': last_appointment.appointment_time,
                    'appointment_id': last_appointment.appointment_id,
                    'specialization': last_appointment.specialization.specialization if last_appointment.specialization else 'N/A',
                    
                })
            return result
    
    def get_pending_appointments(self,obj):
        today = timezone.localdate()
        appointments = obj.appointment_header.filter(
            appointment_status__in=['initiated_by_doctor'],
            appointment_date__gte=today
        ).order_by('appointment_date', 'appointment_time')
        return [{
            'appointment_id': appointment.appointment_id,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'doctor_name': appointment.doctor.first_name + ' ' + appointment.doctor.last_name if appointment.doctor else 'N/A',
            'status': appointment.appointment_status,
            'specialization': appointment.specialization.specialization if appointment.specialization else 'N/A',
            'meeting_link': appointment.meeting_link,
            'type_booking':"Couples" if appointment.is_couple else "Individual",
        } for appointment in appointments]
    
    
    def get_upcoming_appointments(self, obj):
        today = timezone.localdate()
        appointments = obj.appointment_header.filter(
            appointment_status__in=['confirmed'],
            appointment_date__gte=today
        ).order_by('appointment_date', 'appointment_time')
        return [{
            'appointment_id': appointment.appointment_id,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'doctor_name': appointment.doctor.first_name + ' ' + appointment.doctor.last_name if appointment.doctor else 'N/A',
            'status': appointment.appointment_status,
            'specialization': appointment.specialization.specialization if appointment.specialization else 'N/A',
            'meeting_link': appointment.meeting_link,
            'type_booking':"Couples" if appointment.is_couple else "Individual",
        } for appointment in appointments]
    

    def get_previous_appointments(self, obj):
        appointments = obj.appointment_header.filter(appointment_status__in=['completed', 'cancelled']).order_by('-appointment_date', '-appointment_time')
        return [{
            'appointment_id': appointment.appointment_id,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'doctor_name': appointment.doctor.first_name +' ' + appointment.doctor.last_name if appointment.doctor else 'N/A',
            'status': appointment.appointment_status,
            'specialization': appointment.specialization if appointment.specialization else 'N/A',
            'type_booking':"Couples" if appointment.is_couple else "Individual",

        } for appointment in appointments]
