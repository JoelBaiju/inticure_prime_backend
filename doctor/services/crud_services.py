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
from ..models import (
    DoctorProfiles,
    DoctorAppointment,
    DoctorPaymentRules,    
)

# Serializers
from ..serializers import (
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




def update_customer_details(data: dict):
    """
    Update customer profile and related details.
    Returns (success, message or error).
    """
    customer_id = data.get("customer")
    try:
        customer = CustomerProfile.objects.get(id=customer_id)
    except CustomerProfile.DoesNotExist:
        return False, "Customer not found."

    message_parts = []

    if data.get("weight"):
        customer.weight = data.get("weight")
        customer.weight_unit = data.get("weight_unit")
        message_parts.append("Weight")

    if data.get("height"):
        customer.height = data.get("height")
        customer.height_unit = data.get("height_unit")
        message_parts.append("Height")

    customer.save()

    if data.get("extra_questions"):
        for question in data.get("extra_questions"):
            Extra_questions_answers.objects.create(
                question_id=question.get("question_id"),
                answer=question.get("answer"),
                customer=customer
            )
        message_parts.append("Extra questions")

    return True, f"{' & '.join(message_parts)} updated successfully."





class ReferralService:

    @staticmethod
    @transaction.atomic
    def create_referral(user, data, customers):
        """
        Create a referral, assign customers, and schedule reminder.
        """
        try:
            doctor = DoctorProfiles.objects.get(user=user)
        except DoctorProfiles.DoesNotExist:
            raise ValueError("Doctor profile not found.")

        data = data.copy()
        data['doctor'] = doctor.doctor_profile_id

        serializer = ReferralSerializerCreate(data=data)
        serializer.is_valid(raise_exception=True)

        referral = serializer.save()

        # Link customers
        for customer_id in customers:
            try:
                customer = CustomerProfile.objects.get(id=customer_id)
                Referral_customer.objects.create(referral=referral, customer=customer)
            except CustomerProfile.DoesNotExist:
                raise ValueError(f"Customer with ID {customer_id} not found.")

        # Schedule reminder (2 days = 172800 seconds)
        schedule_reminder_to_book_appointment.apply_async(
            (None, referral.id,), countdown=172800
        )

        return referral, serializer.data




def create_new_appointment_service(data):
    slot = data.get("slot")
    doctor_id = data.get("doctor")
    appointment_id = data.get("appointment_id")
    appointment_date = data.get("appointment_date")
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

    # Existing appointment & specialization
    o_appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    customer = o_appointment.customer
    if followup:
        specialization=o_appointment.specialization
    else:
        specialization = Specializations.objects.get(specialization_id=specialization_id)

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


    # Create appointment
    appointment = AppointmentHeader.objects.create(
        customer=customer,
        category=o_appointment.category,
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
    send_payment_pending_email_task.delay(
        appointment.appointment_id
    )
    delete_unpaid_appointment.apply_async((appointment.appointment_id,), countdown=900)
    schedule_reminder_to_book_appointment.apply_async((appointment.appointment_id, None), countdown=172800)

    return appointment, AppointmentDetailSerializer(appointment).data







def update_appointment_status(appointment_id: str, completed: bool, reason: str = None):
    if not appointment_id:
        return Response(
            "appointment_id and completion status are required",
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    except AppointmentHeader.DoesNotExist:
        return Response("invalid appointment id", status=status.HTTP_400_BAD_REQUEST)

    if appointment.end_time < timezone.now():
        return Response("Cannot update past appointments", status=status.HTTP_400_BAD_REQUEST)

    mt = Meeting_Tracker.objects.filter(appointment=appointment).first()
    if not mt:
        return Response("Meeting Tracker not found", status=status.HTTP_400_BAD_REQUEST)

    # If marked completed
    if completed:
        if not mt.doctor_joined:
            return Response("You cannot mark completed without attending the meeting.",status=status.HTTP_400_BAD_REQUEST)
        if not mt.customer_1_joined:
            return Response("You cannot mark completed without the customer joining the meeting.",status=status.HTTP_400_BAD_REQUEST)

        appointment.completed = True
        appointment.appointment_status = "completed"

    # If marked incomplete
    else:
        if not reason:
            return Response(
                "Reason required in case of incompletion",
                status=status.HTTP_400_BAD_REQUEST
            )
        if hasattr(appointment, "reason"):
            appointment.reason = reason
        else:
            return Response(
                "Appointment model does not support a reason field.",
                status=status.HTTP_400_BAD_REQUEST
            )

    appointment.save()
    send_prescription_email_task.delay(
        appointment.appointment_id,
    )
    return Response("updated successfully", status=status.HTTP_200_OK)





def get_customer_prescriptions(customer_id: int):
    """
    Returns all prescriptions, notes, and questionnaire answers for a given customer.
    """
    try:
        customer = CustomerProfile.objects.get(id=customer_id)
    except CustomerProfile.DoesNotExist:
        return None, "invalid customer id"

    # Query prescriptions/notes
    tests = Prescribed_Tests.objects.filter(customer=customer)
    medicines = Prescribed_Medications.objects.filter(customer=customer)
    patient_notes = Notes_for_patient.objects.filter(customer=customer)
    observation_notes = Observation_Notes.objects.filter(customer=customer)
    followup_advices = Follow_Up_Notes.objects.filter(customer=customer)

    # Serialize them (return empty [] if none)
    data = {
        "tests": PrescribedTestsSerializer(tests, many=True).data if tests else [],
        "medicine": PrescribedMedicationsSerializer(medicines, many=True).data if medicines else [],
        "patient_notes": NotesForPatientSerializer(patient_notes, many=True).data if patient_notes else [],
        "observation_notes": ObservationNotesSerializer(observation_notes, many=True).data if observation_notes else [],
        "followup_advices": Followup_notes_serializer(followup_advices, many=True).data if followup_advices else [],
        "patient_details": PatientSerializer(customer).data,
        "patient_first_name": customer.user.first_name,
        "patient_last_name": customer.user.last_name,
    }

    # Questionnaire answers
    questionnaire_answers = AppointmentQuestionsAndAnswers.objects.filter(customer=customer)
    data["questionnaire_answers"] = GroupedQuestionAnswerSerializer.from_queryset(questionnaire_answers)

    # Extra questions/answers
    answers = {
        ans.question_id: ans.answer
        for ans in Extra_questions_answers.objects.filter(customer=customer)
    }
    data["extra_questions"] = [
        {"question": q.question, "question_id": q.id, "answer": answers.get(q.id)}
        for q in Extra_questions.objects.all()
    ]

    return data, None
