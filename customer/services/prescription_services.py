from collections import defaultdict
from django.conf import settings

from analysis.models import (
    Prescribed_Medications, Prescribed_Tests, 
    Notes_for_patient, Follow_Up_Notes, AppointmentHeader
)
from customer.models import Suggested_packages
from doctor.models import DoctorPaymentRules
from customer.serializers import (
    PrescribedMedicationsSerializer, PrescribedTestsSerializer,
    NotesForPatientSerializer, Followup_notes_serializer,
    PatientSerializer
)
from doctor.serializers import DoctorPaymentRulesSerializer


class PrescriptionService:
    @staticmethod
    def get_customer_prescriptions(customer):
        """Get all prescriptions for customer grouped by doctor"""
        # Get prescription data
        tests = Prescribed_Tests.objects.filter(
            customer=customer, submitted=False
        ).select_related("doctor")
        
        medicines = Prescribed_Medications.objects.filter(
            customer=customer, is_active=True
        ).select_related("doctor")
        
        patient_notes = Notes_for_patient.objects.filter(
            customer=customer
        ).select_related("doctor")

        # Serialize data
        tests_data = [PrescribedTestsSerializer(test).data for test in tests]
        medicines_data = [PrescribedMedicationsSerializer(med).data for med in medicines]
        notes_data = [NotesForPatientSerializer(note).data for note in patient_notes]

        # Group by doctor
        prescriptions_per_doctor = defaultdict(lambda: {
            "doctor": None, 
            "medicines": [], 
            "tests": [], 
            "notes": []
        })

        for medicine in medicines_data:
            prescriptions_per_doctor[medicine['doctor_id']]['medicines'].append(medicine)
            prescriptions_per_doctor[medicine['doctor_id']]['doctor'] = medicine['doctor']

        for test in tests_data:
            prescriptions_per_doctor[test['doctor_id']]['tests'].append(test)
            prescriptions_per_doctor[test['doctor_id']]['doctor'] = test['doctor']

        for note in notes_data:
            prescriptions_per_doctor[note['doctor_id']]['notes'].append(note)
            prescriptions_per_doctor[note['doctor_id']]['doctor'] = note['doctor']

        # Convert to list format
        return list(prescriptions_per_doctor.values())

    @staticmethod
    def generate_prescription_context(customer, doctor):
        """Generate context data for prescription PDF"""
        # Get latest completed appointment
        # latest_appointment = AppointmentHeader.objects.filter(
        #     customer=customer, 
        #     doctor=doctor, 
        #     completed=True
        # ).latest('start_time')

        # Get prescription data for specific doctor
        tests = Prescribed_Tests.objects.filter(
            customer=customer, doctor=doctor, submitted=False
        ).select_related("doctor")
        
        medicines = Prescribed_Medications.objects.filter(
            customer=customer, doctor=doctor, is_active=True
        ).select_related("doctor")
        
        patient_notes = Notes_for_patient.objects.filter(
            customer=customer, doctor=doctor
        ).select_related("doctor")
        
        follow_notes = Follow_Up_Notes.objects.filter(
            customer=customer, appointment__doctor=doctor
        )

        # Serialize data
        tests_data = PrescribedTestsSerializer(tests, many=True).data
        medicines_data = PrescribedMedicationsSerializer(medicines, many=True).data
        notes_data = NotesForPatientSerializer(patient_notes, many=True).data
        follow_notes_data = Followup_notes_serializer(follow_notes, many=True).data
        customer_data = PatientSerializer(customer).data

        # Get doctor specializations
        doctor_specializations = [
            spec.specialization.specialization 
            for spec in doctor.doctor_specializations.all()
        ]

        return {
            "medicines": medicines_data,
            "tests": tests_data,
            "notes": notes_data,
            "follow_notes": follow_notes_data,
            "patient_first_name": customer.user.first_name,
            "patient_last_name": customer.user.last_name,
            "patient_details": customer_data,
            "doctor_name": f"{doctor.first_name} {doctor.last_name}".strip(),
            "doctor_specializations": doctor_specializations,
            'doctor_qualification': doctor.qualification,
            "reg_no": doctor.registration_number,
            "salutation": doctor.salutation,
            "doctor_phone": doctor.mobile_number if doctor.mobile_number else ' ',
            "doctor_email": doctor.email_id,
            'doctor_signature': doctor.sign_file_name.url if doctor.sign_file_name else None,
            "backend_url": settings.BACKEND_URL,
            "consultation_type": 'Video',
            # "status": latest_appointment.followup,
            "status": "hello",
            'date': "haiiaiai"
            # 'date': latest_appointment.start_time.date()
        }

    @staticmethod
    def get_doctor_packages(doctor, specialization, customer):
        """Get available packages for doctor with suggestion flags"""
        packages = DoctorPaymentRules.objects.filter(
            doctor=doctor, 
            specialization=specialization, 
            country=customer.country_details
        )
        
        serialized_packages = DoctorPaymentRulesSerializer(packages, many=True).data
        
        # Add suggested flag to each package
        for package in serialized_packages:
            suggested = Suggested_packages.objects.filter(
                suggested_by=doctor,
                customer=customer,
                package_id=package['id']
            ).exists()
            package['suggested'] = suggested

        return serialized_packages