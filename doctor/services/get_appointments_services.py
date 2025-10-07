from datetime import datetime
from collections import defaultdict

from django.utils import timezone
from django.shortcuts import get_object_or_404

from doctor.models import (
    DoctorProfiles,
    DoctorAppointment,

)
from general.utils import convert_utc_to_local_return_dt

from customer.models import (
    CustomerProfile,
    Extra_questions,
    Extra_questions_answers,
)

from analysis.models import (
    AppointmentQuestionsAndAnswers,
    Doctor_Suggested_Plans,
    Observation_Notes,
    Prescribed_Medications,
    Prescribed_Tests,
    Follow_Up_Notes,
    Notes_for_patient,
    Appointment_customers,
    Referral_customer,
    Meeting_Tracker,
    AppointmentHeader,
    Questionnaire,
    Options
)

from analysis.serializers import QuestionnaireSerializer, OptionsSerializer

from ..serializers import (
    AppointmentDetailSerializer,
    PatientSerializer,
    GroupedQuestionAnswerSerializer,
    ReferralSerializer,
    SuggestedPlanSerializer,
    ObservationNotesSerializer,
    PrescribedMedicationsSerializer,
    PrescribedTestsSerializer,
    Followup_notes_serializer,
    NotesForPatientSerializer,
)

def get_doctor_or_none(user):
    try:
        return DoctorProfiles.objects.get(user=user)
    except DoctorProfiles.DoesNotExist:
        return None


def format_appointment(appt, doctor, include_meeting=False):
    """Format an appointment object into dict for API response."""
    today = timezone.now().date()

    customer_name = (
        f"{appt.customer.user.first_name} {appt.customer.user.last_name}"
        if appt and appt.customer else "Unknown"
    )
    appt_type = "Couple" if appt and appt.is_couple else "Individual"
    time_str = convert_utc_to_local_return_dt(appt.start_time, doctor.time_zone) if appt.start_time else "N/A"

    # Duration calculation
    if appt.start_time and appt.end_time:
        if appt.start_time.tzinfo and appt.end_time.tzinfo:
            duration_minutes = int((appt.end_time - appt.start_time).total_seconds() // 60)
        else:
            duration_minutes = int(
                (datetime.combine(today, appt.end_time) - datetime.combine(today, appt.start_time)).total_seconds() // 60
            )
        duration = f"{duration_minutes} mins"
    else:
        duration = "Unknown"

    specialization_name = appt.specialization.specialization if appt.specialization else "General"

    data = {
        "appointment_id": appt.appointment_id if appt else None,
        "name": customer_name,
        "type": appt_type,
        "time": time_str.time(),
        "duration": duration,
        "specialization": specialization_name,
        "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
        "followup": bool(appt.followup),
        "date": convert_utc_to_local_return_dt(appt.start_time, doctor.time_zone).date(),
        "is_couple": getattr(appt, "is_couple", False)
    }

    if include_meeting:
        try:
            data["meeting_link"] = Meeting_Tracker.objects.get(appointment=appt).doctor_meeting_link
        except Meeting_Tracker.DoesNotExist:
            data["meeting_link"] = None

    return data


def get_appointments_data(doctor, limit=3):
    """Return categorized appointments for doctor dashboard."""
    now = timezone.now()

    upcoming_qs = AppointmentHeader.objects.filter(
        doctor=doctor,
        appointment_status="confirmed",
        completed=False,
        start_time__gte=now
    ).order_by("start_time")

    previous_qs = AppointmentHeader.objects.filter(
        doctor=doctor,
        appointment_status__in=["confirmed", "completed"],
        completed=True,
        start_time__lte=now
    ).order_by("-start_time")

    missed_qs = AppointmentHeader.objects.filter(
        doctor=doctor,
        appointment_status__in=["confirmed", "completed"],
        completed=False,
        start_time__lte=now
    ).order_by("-start_time")

    rescheduled_qs = AppointmentHeader.objects.filter(
        doctor=doctor,
        appointment_status__in=["rescheduled_by_customer", "rescheduled_by_doctor"],
        completed=False
    ).order_by("start_time")

    return {
        "upcoming_appointments": [format_appointment(a, doctor, include_meeting=True) for a in upcoming_qs],
        "previous_appointments": [format_appointment(a, doctor) for a in previous_qs],
        "missed_appointments": [format_appointment(a, doctor) for a in missed_qs],
        "rescheduled_appointments": [
            {**format_appointment(a, doctor), "rescheduled_by": a.appointment_status}
            for a in rescheduled_qs
        ],
    }




def get_appointment_full_details_service(appointment_id):
    appointment = get_object_or_404(AppointmentHeader, appointment_id=appointment_id)
    customer = appointment.customer
    customers = CustomerProfile.objects.filter(appointment_customers__appointment=appointment)

    # Core info
    appointment_data = AppointmentDetailSerializer(appointment).data
    patient_data = PatientSerializer(customers, many=True).data

    # Questionnaire
    questionnaire_answers = AppointmentQuestionsAndAnswers.objects.filter(customer=customer)
    grouped_answers = GroupedQuestionAnswerSerializer.from_queryset(questionnaire_answers)

    # Extra questions
    answers = {
        ans.question_id: ans.answer
        for ans in Extra_questions_answers.objects.filter(customer=customer)
    }
    extra_questions = [
        {"question": q.question, "question_id": q.id, "answer": answers.get(q.id)}
        for q in Extra_questions.objects.all()
    ]

    # Medical data
    suggested_plans = Doctor_Suggested_Plans.objects.filter(refferral=appointment.referral)
    notes = Observation_Notes.objects.filter(customer=customer)
    medications = Prescribed_Medications.objects.filter(customer=customer)
    tests = Prescribed_Tests.objects.filter(customer=customer)
    followup_notes = Follow_Up_Notes.objects.filter(customer=customer)
    notes_for_patient = Notes_for_patient.objects.filter(customer=customer)

    # Next appointment or referral checks
    today = timezone.now().date()
    next_appointment_booked = Appointment_customers.objects.filter(
        appointment__doctor=appointment.doctor,
        appointment__start_time__gt=appointment.start_time,
        customer=customer
    ).exists()

    referred_today = Referral_customer.objects.filter(
        referral__doctor=appointment.doctor,
        customer=customer,
        referral__referred_date__date=today
    ).exists()

    added_ob_notes = Observation_Notes.objects.filter(appointment=appointment).exists()
    added_fup_notes = Follow_Up_Notes.objects.filter(appointment=appointment).exists()

    questionnaire = Questionnaire.objects.all()
    print("Questionnaire:", questionnaire)
    questionnaire_serialized = QuestionnaireSerializer(questionnaire, many=True).data

    for question in questionnaire_serialized:
        
        question['options']= OptionsSerializer(
            Options.objects.filter(question=question['id']),
            many=True
        ).data
        for opt in question['options']:
            opt['is_selected']= True if AppointmentQuestionsAndAnswers.objects.filter(
                question_id=question['id'],
                answer_id=opt['id'],
                customer=customer
            ).exists() else False

    return {
        "booked_customer":appointment.customer.id,
        "appointment": appointment_data,
        "patients": patient_data,
        "questionnaire_answers": grouped_answers,
        "extra_questions": extra_questions,
        "referral": ReferralSerializer(appointment.referral).data if appointment.referral else None,
        "suggested_plans": SuggestedPlanSerializer(suggested_plans, many=True).data,
        "notes": ObservationNotesSerializer(notes, many=True).data,
        "prescribed_medicines": PrescribedMedicationsSerializer(medications, many=True).data,
        "prescribed_tests": PrescribedTestsSerializer(tests, many=True).data,
        "followup_notes": Followup_notes_serializer(followup_notes, many=True).data,
        "notes_for_patient": NotesForPatientSerializer(notes_for_patient, many=True).data,
        "nextbooked_or_refered": next_appointment_booked or referred_today,
        "added_ob_notes": added_ob_notes,
        "added_fup_notes": added_fup_notes,
        "doctor_id": appointment.doctor.doctor_profile_id,
        "is_prescription_allowed": appointment.doctor.is_prescription_allowed,
        'is_couple':appointment.is_couple,
        "habitual_questions":questionnaire_serialized
    }
