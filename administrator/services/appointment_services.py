from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

# Models
from customer.models import (
    CustomerProfile,
    Extra_questions_answers,
    Extra_questions,
    Customer_Package
)
from doctor.models import DoctorProfiles
from analysis.models import (
    AppointmentHeader,
    Meeting_Tracker,
    Referral,
    Referral_customer,
    Prescribed_Tests,
    Prescribed_Medications,
    Notes_for_patient,
    Observation_Notes,
    Follow_Up_Notes,
    AppointmentQuestionsAndAnswers,
    Appointment_customers,

)
from administrator.models import *
from doctor.models import (
    DoctorProfiles,
    DoctorAppointment,
    DoctorPaymentRules,    
)

# Serializers
from doctor.serializers import (
    ReferralSerializerCreate,
    AppointmentDetailSerializer,
    PrescribedTestsSerializer,
    PrescribedMedicationsSerializer,
    NotesForPatientSerializer,
    ObservationNotesSerializer,
    Followup_notes_serializer,
    PatientSerializer,
    GroupedQuestionAnswerSerializer,
)

# Tasks & Utils
from general.tasks import schedule_reminder_to_book_appointment, send_payment_pending_email_task, send_prescription_email_task
from analysis.tasks import delete_unpaid_appointment
from general.utils import convert_local_dt_to_utc
from general.emal_service import send_payment_pending_email
from general.notification_controller import send_payment_pending_notification







def create_new_appointment_service(data):
    slot = data.get("slot")
    doctor_id = data.get("doctor")
    language_pref = data.get("language_pref")
    gender_pref = data.get("gender_pref")
    specialization_id = data.get("specialization")
    is_couple = data.get("is_couple", False)
    referal_id = data.get("referal_id")
    followup = data.get("followup")
    followup_remark = data.get("followup_remark")
    customers = data.get("customers", [])
    include_package = data.get("include_package", False)
    package_id = data.get("package_id")
    payment_required_by_admin = data.get("payment_required", True)
    customer_id = data.get("customer_id")
    appointment_id = data.get("appointment_id")
    
    # Existing appointment & specialization
    customer = CustomerProfile.objects.get(id=customer_id)

    if followup:

        o_appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        specialization=o_appointment.specialization
    else:
        o_appointment = None
        try:
            specialization = Specializations.objects.get(specialization_id=specialization_id)
        except:
            specialization = Specializations.objects.filter(specialization="No Specialization").first()
    # Doctor
    doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)

    # Convert slot times to UTC
    start_datetime_utc = convert_local_dt_to_utc(slot.get("start"), doctor.time_zone)
    end_datetime_utc = convert_local_dt_to_utc(slot.get("end"), doctor.time_zone)

    # Overlap check
    overlapping = DoctorAppointment.objects.filter(
        doctor=doctor,
        start_time__lt=end_datetime_utc,
        end_time__gt=start_datetime_utc,
    ).exists()
    if overlapping:
        raise Exception("The selected time slot overlaps with an existing appointment.")

    # Package
    
    payment_rule = None
    package = None
    if include_package:
        print(package_id)
        payment_rule = DoctorPaymentRules.objects.get(id=package_id)
    
    if payment_required_by_admin:
        try:
            package = Customer_Package.objects.filter(
                customer = customer,
                specialization = specialization,
                doctor = doctor,
                is_couple = is_couple,
                appointments_left__gt = 0,
                expires_on__gt = timezone.now()
            ).first()
            print(customer , doctor , is_couple , specialization)
            print(package)
            if package:
                payment_required = False
                payment_done = True
                package.appointments_left-=1
                package.save()
            else:
                payment_done= False
                payment_required = True
        
        except Exception as e :
            print(e)
            print(customer , doctor , is_couple , specialization)
            payment_required =True
            payment_done = False
    else:
        payment_required = False
        payment_done = True


    # Create appointment
    appointment = AppointmentHeader.objects.create(
        customer=customer,
        category=o_appointment.category if o_appointment else None,
        gender_pref=gender_pref.get("value") if gender_pref else None,
        appointment_status='confirmed' if payment_done else "pending_payment",
        status_detail="initiated by doctor waiting for payment",
        start_time=start_datetime_utc,
        end_time=end_datetime_utc,
        doctor=doctor,
        customer_message=data.get("message"),
        language_pref=language_pref.get("value") if language_pref else None,
        specialization=specialization,
        is_couple=is_couple,
        referral=Referral.objects.get(id=referal_id) if referal_id else None,
        is_referred=True if referal_id else False,
        booked_by="doctor",
        followup=True if followup else False,
        followup_remark=followup_remark if followup else None,
        followup_of_appointment=o_appointment,
        payment_rule=payment_rule if include_package else None,
        package_included=include_package,
        payment_done = payment_done,
        payment_required = payment_required,
        package = package,
        package_used = True if package else False
      
    )

    # Add customers
    for customer_id in customers:
        customer = CustomerProfile.objects.get(id=customer_id)
        Appointment_customers.objects.create(appointment=appointment, customer=customer)

    if customers == []:
        Appointment_customers.objects.create(appointment=appointment, customer=customer)
    # Update referral if used
    if referal_id:
        Referral.objects.filter(id=referal_id).update(converted_to_appointment=True)

    # Create doctor’s appointment block
    DoctorAppointment.objects.create(
        doctor=doctor,
        specialization=specialization,
        start_time=start_datetime_utc,
        end_time=end_datetime_utc,
        appointment=appointment,
    )

    # Email + async tasks
    if not appointment.payment_done :
        send_payment_pending_notification.delay(
            appointment.appointment_id
        )
    delete_unpaid_appointment.apply_async((appointment.appointment_id,), countdown=900)
    schedule_reminder_to_book_appointment.apply_async((appointment.appointment_id, None), countdown=172800)

    return appointment, AppointmentDetailSerializer(appointment).data


    
