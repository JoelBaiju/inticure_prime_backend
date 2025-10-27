# serializers.py
from sqlite3 import converters
from rest_framework import serializers
from .models import CustomerProfile
from collections import defaultdict
from django.utils import timezone
from analysis.models import Referral , Referral_customer
from general.utils import Appointment_actions , convert_utc_to_local_return_dt
from datetime import datetime, date as dt_date, timedelta
from django.db.models import Q
from analysis.models import AppointmentHeader , Meeting_Tracker


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        read_only_fields = ['user']  # user will be set from the request
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class CustomerProfileSerializerMini(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = CustomerProfile
        fields = ['first_name','last_name','id']
       





from collections import defaultdict
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers


class CustomerPreviousAppointmentsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    previous_appointments = serializers.SerializerMethodField()
    country = serializers.CharField(source='country_details.country_name', read_only=True)
    partner_first_name = serializers.CharField(source='partner.user.first_name', read_only=True, default=None)
    partner_last_name = serializers.CharField(source='partner.user.last_name', read_only=True, default=None)
    partner_email = serializers.EmailField(source='partner.email', read_only=True, default=None)
    partner_mobile_number = serializers.CharField(source='partner.whatsapp_number', read_only=True, default=None)

    class Meta:
        model = CustomerProfile
        fields = [
            'user', 'id', 'gender', 'previous_appointments',
            'first_name', 'last_name', 'email', 'whatsapp_number', 'country_code',
            'completed_first_analysis',  'country',
            'preferred_name',
            'partner_first_name', 'partner_last_name', 'date_of_birth',
            'partner_email', 'partner_mobile_number'
        ]


    def get_previous_appointments(self, obj):
        now = timezone.now()
        appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                Q(appointment_status__in=['completed', 'cancelled'])| Q(start_time__lt=now),
                Q(doctor__doctor_flag = "senior")
            )
            .select_related("doctor", "specialization")
            .order_by("-start_time")
            .distinct()
        )
        result = []
        for appt in appointments:
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f" {appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "booked_by": appt.booked_by,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
                "salutation": appt.doctor.salutation if appt.doctor else None,
            })
        return result






from general.finance.calculators import first_consultation_cost_calculator


class CustomerDashboardSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    currently_consulting_doctors = serializers.SerializerMethodField()
    upcoming_appointments = serializers.SerializerMethodField()
    previous_appointments = serializers.SerializerMethodField()
    country = serializers.CharField(source='country_details.country_name', read_only=True)
    pending_appointments = serializers.SerializerMethodField()
    referred_doctors = serializers.SerializerMethodField()
    rescheduled_appointments = serializers.SerializerMethodField()
    followup_appointments = serializers.SerializerMethodField()
    cancelled_appointments = serializers.SerializerMethodField()
    partner_first_name = serializers.CharField(source='partner.user.first_name', read_only=True, default=None)
    partner_last_name = serializers.CharField(source='partner.user.last_name', read_only=True, default=None)
    partner_email = serializers.EmailField(source='partner.email', read_only=True, default=None)
    partner_mobile_number = serializers.CharField(source='partner.whatsapp_number', read_only=True, default=None)
    whatsapp_confirmation = serializers.SerializerMethodField()
    email_confirmation = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = [
            'user', 'id', 'gender', 'previous_appointments', 'upcoming_appointments',
            'first_name', 'last_name', 'email', 'whatsapp_number', 'country_code',
            'completed_first_analysis', 'currently_consulting_doctors', 'country',
            'preferred_name', 'pending_appointments', 'referred_doctors',
            'rescheduled_appointments', 'followup_appointments', 'cancelled_appointments',
            'partner_first_name', 'partner_last_name', 'date_of_birth',
            'partner_email', 'partner_mobile_number', 'whatsapp_confirmation', 'email_confirmation'
        ]

    def get_whatsapp_confirmation(self, obj):
        return obj.confirmation_method in ['WhatsApp', 'whatsapp', 'both']

    def get_email_confirmation(self, obj):
        return obj.confirmation_method in ['Email', 'email', 'both']

    def get_currently_consulting_doctors(self, obj):
        appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                file_is_open=True
            )
            .select_related("doctor", "specialization")
            .order_by('-start_time')
            .distinct()
        )
        doctor_appointments = defaultdict(list)
        for appointment in appointments:
            doctor_appointments[appointment.doctor].append(appointment)

        result = []
        for doctor, appts in doctor_appointments.items():
            last_appointment = max(appts, key=lambda x: x.start_time)
            local_dt = convert_utc_to_local_return_dt(last_appointment.start_time, obj.time_zone)
            result.append({
                'doctor_id': doctor.doctor_profile_id,
                'doctor_name': f" {doctor.first_name} {doctor.last_name}".strip(),
                'last_appointment_date': local_dt.date(),
                'last_appointment_time': local_dt.time(),
                'appointment_id': last_appointment.appointment_id,
                'specialization': last_appointment.specialization.specialization if last_appointment.specialization else 'N/A',
                'salutation': doctor.salutation
            })
        return result

    def get_pending_appointments(self, obj):
        today = timezone.now()
        appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                appointment_status__in=['initiated_by_doctor', 'pending_payment', 'pending_slot'],
                start_time__gt=today,
                followup=False
            )
            .select_related("doctor", "specialization")
            .order_by("start_time")
            .distinct()
        )
        result = []
        for appt in appointments:
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f" {appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "specialization_id": appt.specialization.specialization_id if appt.specialization else "N/A",
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "actions": Appointment_actions(appt.appointment_id),
                "booked_by": appt.booked_by,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "is_couple": appt.is_couple,
                "package_included": appt.package_included,
                "salutation": appt.doctor.salutation if appt.doctor else None,
                "price_details": first_consultation_cost_calculator(appointment_id=appt.appointment_id)['total_cost'],
                "currency": appt.customer.country_details.currency_symbol,
            })
        return result

    def get_upcoming_appointments(self, obj):
        now = timezone.now()
        appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                appointment_status="confirmed",
                completed=False,
                end_time__gte=now
            )
            .select_related("doctor", "specialization", "package")
            .order_by("start_time")
            .distinct()
        )
        result = []
        for appt in appointments:
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            tracker = Meeting_Tracker.objects.get(appointment = appt)
            ttd = appt.temporary_transaction_data.first()
            payment_id = None
            if ttd:
                if ttd.stripe_transactions.exists():
                    payment_id = ttd.stripe_transactions.first().stripe_payment_intent_id
                elif ttd.razorpay_transactions.exists():
                    payment_id = ttd.razorpay_transactions.first().razorpay_payment_id
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f" {appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "specialization_id": appt.specialization.specialization_id if appt.specialization else "N/A",
                "meeting_link": tracker.customer_1_meeting_id if tracker.customer_1 == obj else tracker.customer_2_meeting_id if tracker.customer_2 == obj else None,
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "booked_by": appt.booked_by,
                "is_couple": appt.is_couple,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "package_used": appt.package_used,
                "appointments_left_in_package": appt.package.appointments_left if appt.package else 0,
                "salutation": appt.doctor.salutation if appt.doctor else None,
                "payment_amount": ttd.total_amount if ttd else None,
                "currency": ttd.currency if ttd else None,
                "gateway": ttd.gateway if ttd else None,
                "payment_id": payment_id
            })
        return result

    def get_previous_appointments(self, obj):
        now = timezone.now()
        appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                Q(appointment_status__in=['completed', 'cancelled'])| Q(end_time__lt=now),
            )
            .select_related("doctor", "specialization")
            .order_by("-start_time")
            .distinct()
        )
        result = []
        for appt in appointments:
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f" {appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "booked_by": appt.booked_by,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
                "salutation": appt.doctor.salutation if appt.doctor else None,
            })
        return result

    def get_referred_doctors(self, obj):
        referals = (
            Referral.objects.filter(
                referral_customers__customer=obj,
                converted_to_appointment=False
            )
            .select_related("referred_doctor", "specialization", "doctor")
            .order_by("-referred_date")
            .distinct()
        )
        result = []
        for refer in referals:
            local_dt = convert_utc_to_local_return_dt(refer.referred_date, obj.time_zone)
            result.append({
                "referred_doctor": f"{refer.referred_doctor.first_name} {refer.referred_doctor.last_name}",
                "referred_doctor_id": refer.referred_doctor.doctor_profile_id,
                "referred_specialization": refer.specialization.specialization if refer.specialization else None,
                "referred_specialization_id": refer.specialization.specialization_id if refer.specialization else None,
                "referred_date": local_dt.date(),
                "referral_notes": refer.referral_notes,
                "referred_by": f"{refer.doctor.first_name} {refer.doctor.last_name}",
                "is_couple": refer.is_couple,
                "id": refer.id,
                "salutation": refer.doctor.salutation,
                "salutation_2nd_doctor": refer.referred_doctor.salutation
                
            })
        return result

    def get_rescheduled_appointments(self, obj):
        now = timezone.now()
        rescheduled = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                appointment_status__in=['rescheduled_by_customer', 'rescheduled_by_doctor'],
                end_time__gte=now
            )
            .select_related("doctor", "specialization")
            .order_by("-start_time")
            .distinct()
        )
        result = []
        for appt in rescheduled:
            latest_reschedule = appt.reschedule_history.order_by("-initiated_on").first()
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f"{appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "specialization_id": appt.specialization.specialization_id if appt.specialization else "N/A",
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "booked_by": appt.booked_by,
                "is_couple": appt.is_couple,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "rescheduled_on": convert_utc_to_local_return_dt(latest_reschedule.initiated_on, obj.time_zone)
                                   if latest_reschedule else None,
                "rescheduled_by": latest_reschedule.initiated_by if latest_reschedule else None,
                "reschedule_reason": latest_reschedule.reason if latest_reschedule else None,
                "salutation": appt.doctor.salutation if appt.doctor else None,
                
            })
        return result

    def get_followup_appointments(self, obj):
        followup_appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                followup=True
            )
            .exclude(
                appointment_status__in=[
                    'confirmed', 'completed', 'cancelled', "cancelled_by_admin",
                    "cancelled_by_customer", 'rescheduled_by_doctor', 'rescheduled_by_customer'
                ]
            )
            .select_related("doctor", "specialization", "package")
            .order_by("-start_time")
            .distinct()
        )
        result = []
        for appt in followup_appointments:
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f" {appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "specialization_id": appt.specialization.specialization_id if appt.specialization else "N/A",
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "booked_by": appt.booked_by,
                "actions": Appointment_actions(appt.appointment_id),
                "is_couple": appt.is_couple,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "package_included": appt.package_included,
                "session_count": appt.package.appointments_left if appt.package else None,
                "salutation": appt.doctor.salutation if appt.doctor else None,
                "price_details":first_consultation_cost_calculator(appointment_id=appt.appointment_id)['total_cost'],
                "currency":appt.customer.country_details.currency_symbol

            })
        return result

    def get_cancelled_appointments(self, obj):
        cancelled_appointments = (
            AppointmentHeader.objects.filter(
                Q(appointment_customers__customer=obj) | Q(customer=obj),
                appointment_status__in=['cancelled', "cancelled_by_admin", "cancelled_by_customer"]
            )
            .select_related("doctor", "specialization", "package")
            .order_by("-start_time")
            .distinct()
        )
        result = []
        for appt in cancelled_appointments:
            local_dt = convert_utc_to_local_return_dt(appt.start_time, obj.time_zone)
            result.append({
                "appointment_id": appt.appointment_id,
                "appointment_date": local_dt.date(),
                "appointment_time": local_dt.time(),
                "doctor_name": f" {appt.doctor.first_name} {appt.doctor.last_name}".strip()
                                if appt.doctor else "N/A",
                "status": appt.appointment_status,
                "specialization": appt.specialization.specialization if appt.specialization else "N/A",
                "type_booking": "Couples" if appt.is_couple else "Individual",
                "booked_by": appt.booked_by,
                "actions": Appointment_actions(appt.appointment_id),
                "is_couple": appt.is_couple,
                "doctor_id": appt.doctor.doctor_profile_id if appt.doctor else None,
                "package_included": appt.package_included,
                "session_count": appt.package.appointments_left if appt.package else None,
                "salutation": appt.doctor.salutation if appt.doctor else None,
            })
        return result





from analysis.models import Prescribed_Medications,Prescribed_Tests,Notes_for_patient,Follow_Up_Notes







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
    doctor_id = serializers.IntegerField(source='doctor.doctor_profile_id', read_only=True)
    class Meta:
        model = Prescribed_Medications
        fields = ['id' , 'doctor' , 'medicine_name' ,'dosage' ,'strength' , 'frequency' , 'duration' ,'instruction' ,'doctor_id' ]
     
    def get_doctor(self, obj):
        first = obj.doctor.first_name
        last = obj.doctor.last_name
        return f"{first} {last}".strip()





class PrescribedTestsSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    doctor_id = serializers.IntegerField(source='doctor.doctor_profile_id', read_only=True)
    class Meta:
        model = Prescribed_Tests
        fields = ['id' , 'doctor' , 'test_name' ,'instruction' ,'doctor_id' ]
    
    def get_doctor(self, obj):
        first = obj.doctor.first_name
        last = obj.doctor.last_name
        return f"{first} {last}".strip()



class NotesForPatientSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    doctor_id = serializers.IntegerField(source='doctor.doctor_profile_id', read_only=True)
    class Meta:
        model = Notes_for_patient
        fields = ['id' , 'doctor' , 'note' , 'created_at' ,'doctor_id' ]
    
    def get_doctor(self, obj):
        first = obj.doctor.first_name
        last = obj.doctor.last_name
        return f"{first} {last}".strip()



class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.first_name')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    date_of_birth = serializers.DateField( format='%d-%m-%Y', input_formats=['%d-%m-%Y', '%Y-%m-%d'])
    class Meta:
        model = CustomerProfile
        fields = [
            'username', 'first_name', 'last_name', 'preferred_name', 'gender','id',
            'weight', 'height','height_unit','weight_unit', 'mobile_number', 'address', 'profile_pic', 'date_of_birth'
        ]



from administrator.models import Specializations

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specializations
        fields = '__all__'




class SpecializationsSerializerFull(serializers.ModelSerializer):
    double_session_duration = serializers.SerializerMethodField()
    single_session_duration = serializers.SerializerMethodField()
    
    
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
    
    

    def get_single_session_duration(self, obj):
        if not obj.single_session_duration:
            return None

        total_seconds = int(obj.single_session_duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"