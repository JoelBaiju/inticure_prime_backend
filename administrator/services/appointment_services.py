from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


from django.db.models import Q
from general.utils import convert_utc_to_local_return_dt
from ..utils import get_ist_dt , get_payment_details_for_appointment , get_meeting_links_for_appointment , get_reminder_statuses_for_appointment , get_confirmation_date_from_reminders


from customer.models import (
    CustomerProfile,
    Customer_Package
)
from doctor.models import DoctorProfiles
from analysis.models import (
    AppointmentHeader,
    Referral,
   
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
    AppointmentDetailSerializer,
   
)

# Tasks & Utils
from general.tasks import schedule_reminder_to_book_appointment
from analysis.tasks import delete_unpaid_appointment
from general.utils import convert_local_dt_to_utc
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


    










def get_admin_appointments_queryset(params):
    qs = AppointmentHeader.objects.all().select_related(
        "doctor", "customer__user", "specialization"
    ).prefetch_related(
        "reminder_sent_history",
        "temporary_transaction_data__stripe_transactions",
        "temporary_transaction_data__razorpay_transactions",
    )

    status = params.get("status")
    print(status , status)
    if status:
        if status == "completed":
            print("in status" , status)
            status_list = ["completed", "customer_no_show", "doctor_no_show"]
        if status == 'cancelled':
            print("in status" , status)
            status_list = ['cancelled_by_customer','cancelled_by_admin']
        if status == "upcoming":
            print("in status" , status)
            status_list = ["confirmed"]
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        qs = qs.filter(appointment_status__in=status_list)

    specialization = params.get("specialization")
    if specialization:
        if specialization.isdigit():
            qs = qs.filter(
                specialization__specialization_id=int(specialization)
            )
        else:
            qs = qs.filter(
                specialization__specialization__icontains=specialization
            )

    search = params.get("search")
    if search:
        qs = qs.filter(
            Q(appointment_id__icontains=search)
            | Q(doctor__first_name__icontains=search)
            | Q(doctor__last_name__icontains=search)
            | Q(customer__user__first_name__icontains=search)
            | Q(customer__user__last_name__icontains=search)
            | Q(customer__id__icontains=search)
        )

    sort = params.get("sort", "-start_time")
    allowed_sorts = {
        "start_time", "-start_time",
        "booked_on", "-booked_on",
        "appointment_id", "-appointment_id"
    }
    if sort not in allowed_sorts:
        sort = "-start_time"

    return qs.order_by(sort)


def format_admin_appointment(appt):
    customer_obj = getattr(appt, "customer", None)
    patient_tz = getattr(customer_obj, "time_zone", None) if customer_obj else None

    appointment_local_for_patient = (
        convert_utc_to_local_return_dt(appt.start_time, patient_tz)
        if appt.start_time else None
    )
    appointment_in_ist = (
        get_ist_dt(appt.start_time) if appt.start_time else None
    )

    meeting_links = get_meeting_links_for_appointment(appt, customer_obj)
    payment_details = get_payment_details_for_appointment(appt)
    reminder_status = get_reminder_statuses_for_appointment(appt)
    confirmed_on = get_confirmation_date_from_reminders(appt)

    doctor = getattr(appt, "doctor", None)
    doctor_name = salutation = doctor_id = None
    if doctor:
        doctor_name = f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()
        salutation = getattr(doctor, "salutation", None)
        doctor_id = getattr(doctor, "doctor_profile_id", None)

    patient_name = None
    if customer_obj and getattr(customer_obj, "user", None):
        patient_name = (
            f"{customer_obj.user.first_name or ''} "
            f"{customer_obj.user.last_name or ''}".strip()
        )
    elif customer_obj:
        patient_name = getattr(customer_obj, "preferred_name", None)

    return {
        "appointment_id": appt.appointment_id,
        "date": appointment_local_for_patient.date() if appointment_local_for_patient else None,
        "scheduled_time_utc": appt.start_time,
        "start_time": appt.start_time,
        "appointment_time_patient_tz": appointment_local_for_patient,
        "appointment_time_ist": appointment_in_ist,
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "salutation": salutation,
        "patient_id": getattr(customer_obj, "id", None), 
        "patient_name": patient_name,
        "patient_time_zone": patient_tz,
        "doctor_time_zone": getattr(doctor, "time_zone", None),
        "doctor_time" : convert_utc_to_local_return_dt(appt.start_time, getattr(doctor, "time_zone")),
        "consultation_type": "Couples" if appt.is_couple else "Individual",
        "status": appt.appointment_status,
        "confirmed_on": confirmed_on,
        "payment_details": payment_details,
        "booked_by": appt.booked_by,
        "reminder_status": reminder_status,
        "meeting_links": meeting_links,
        "specialization": appt.specialization.specialization if appt.specialization else None,
        "specialization_id": appt.specialization.specialization_id if appt.specialization else None,
        "confirmation_method": getattr(customer_obj, "confirmation_method", None)
        if customer_obj else None,
    }



def get_appointment_counts():
    upcoming = 0
    cancelled = 0 
    completed = 0

    upcoming = AppointmentHeader.objects.filter(appointment_status = "confirmed",
                                                start_time__gt = timezone.now()).count()
    cancelled = AppointmentHeader.objects.filter(appointment_status__in = ["cancelled_by_customer" , "cancelled_by_admin"]).count()
    completed = AppointmentHeader.objects.filter(appointment_status = "completed").count()
    return {
        "upcoming_appts" : upcoming,
        "cancelled_appts" : cancelled,
        "completed_appts" : completed
    }