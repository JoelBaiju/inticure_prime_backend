from .api import whatsapp_api_handler
from analysis.models import AppointmentHeader, Meeting_Tracker
from ..utils import convert_datetime_to_words_in_local_tz



def send_wa_consultation_canceled_by_patient_to_specialist(appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.doctor.time_zone)     
        to_phone        = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number
    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

        
    return whatsapp_api_handler(to_phone, "consultation_canceled_by_patient_to_specialist", parameters)



def send_wa_patient_requested_cancellation (appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        salutation      = appointment.doctor.salutation
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)
        to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."    
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "doctor_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
    ]

    
    return whatsapp_api_handler(to_phone, "patient_requested_cancellation", parameters)




# ====================================================================================================================



def send_wa_welcome_to_inticure (to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]

    
    return whatsapp_api_handler(to_phone, "welcome_to_inticure", parameters)

# ====================================================================================================================


def send_wa_appointment_confirmation(appointment_id):
    try:    
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        salutation      = appointment.doctor.salutation
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)
        meet_link       = Meeting_Tracker.objects.get(appointment=appointment).customer_1_meeting_link
        # to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number
        to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number
        # country_code    = str(appointment.customer.country_code)
    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
        {"type": "text", "parameter_name": "meet_link", "text": meet_link},
    ]
    return whatsapp_api_handler(to_phone, "appointment_confirmation", parameters)






def send_wa_first_consultation_confirmation(appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        salutation      = appointment.doctor.salutation
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)  
        to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number

        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        meet_code       = meeting_tracker.customer_1_meeting_id

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

    button_parameters = [
        {
            "type": "text", 
            "text": meet_code 
        }
    ]
    return whatsapp_api_handler(to_phone, "first_consultation_confirmation", parameters , button_parameters)




def send_wa_consultation_confirmation_to_specialist(appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.doctor.time_zone)
        to_phone        = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number


    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

      
    return whatsapp_api_handler(to_phone, "consultation_confirmation_to_specialist", parameters)




# ====================================================================================================================


def send_wa_auth_code(to_phone, auth_code):
    body_parameters = [
        {"type": "text", "text": auth_code},
    ]
    button_parameters = [
        {
            "type": "text",
            "text": auth_code 
        }
    ]
    
    return whatsapp_api_handler(to_phone, "auth_otp", body_parameters, button_parameters , "en_US")


# ======================================================================================================================




def send_wa_consultation_rescheduled_by_specialist(to_phone, patient_name, salutation, specialist_name, old_date_time, new_date_time):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]

    return whatsapp_api_handler(to_phone, "consultation_rescheduled_by_specialist", parameters)




def send_wa_consultation_rescheduled_by_patient_to_specialist(appointment_id ,  old_date_time, new_date_time):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        salutation = appointment.doctor.salutation
        to_phone = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number
    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "old_datetime", "text": convert_datetime_to_words_in_local_tz(old_date_time , appointment.doctor.time_zone)},
        {"type": "text", "parameter_name": "new_datetime", "text": convert_datetime_to_words_in_local_tz(new_date_time , appointment.doctor.time_zone)},
    ]

        
    return whatsapp_api_handler(to_phone, "consultation_rescheduled_by_patient_to_specialist", parameters)

# ======================================================================================================================


def send_wa_consultation_reminder_24_hours_before(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        specialist_name = appointment.doctor.first_name
        salutation = appointment.doctor.salutation
        tracker = Meeting_Tracker.objects.get(appointment = appointment)
        appt_customers = appointment.appointment_customers.all()
  

        for customer in appt_customers:
            meet_code = tracker.customer_1_meeting_id if customer.customer == tracker.customer_1 else tracker.customer_2_meeting_id
                
            body_parameters = [
                {"type": "text", "text": customer.customer.user.first_name, "parameter_name": "name"},
                {"type": "text", "text": salutation, "parameter_name": "salutation"},
                {"type": "text", "text": specialist_name, "parameter_name": "specialist_name"},
                {"type": "text", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , customer.customer.time_zone), "parameter_name": "date_time"},
            ]
            
            button_parameters = [
                {
                    "type": "text", 
                    "text": meet_code 
                }
            ]
            
            whatsapp_api_handler(f"{customer.customer.whatsapp_country_code}{customer.customer.whatsapp_number}", "consultation_reminder_24_hours_before", body_parameters, button_parameters)

    except AppointmentHeader.DoesNotExist:
        print(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        print("error" , e)
    return "Message sent"





def send_wa_consultation_reminder_1_hour_before (to_phone, patient_name,salutation, specialist_name, date_time, meet_code): 
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "time", "text": date_time},
    ]

        
    button_parameters = [
        {
            "type": "text", 
            "text": meet_code 
        }
    ]

    return whatsapp_api_handler(to_phone, "consultation_reminder_1_hour_before", parameters, button_parameters)



def send_wa_specialist_reminder_1_hour_before(to_phone, patient_name, specialist_name, date_time, meet_code):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

        
    button_parameters = [
        {
            "type": "text", 
            "text": meet_code 
        }
    ]

    return whatsapp_api_handler(to_phone, "specialist_reminder_1_hour_before", parameters, button_parameters)


# ===================================================================================



def send_wa_consultation_reminder_not_yet_scheduled(to_phone, patient_name, salutation, specialist_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]

    
    return whatsapp_api_handler(to_phone, "consultation_reminder_not_yet_scheduled", parameters)


def send_wa_final_consultation_reminder_not_yet_scheduled(to_phone, patient_name, salutation, specialist_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]

    
    return whatsapp_api_handler(to_phone, "final_consultation_reminder_not_yet_scheduled", parameters)



# patient missed
def send_wa_missed_consultation_patient_did_not_join(to_phone, patient_name, salutation, specialist_name, date_time):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

    
    return whatsapp_api_handler(to_phone, "missed_consultation_patient_did_not_join", parameters)



# doctor missed
def send_wa_consultation_interrupted_specialist_emergency(to_phone, patient_name, salutation, specialist_name, date_time):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

    
    return whatsapp_api_handler(to_phone, "consultation_interrupted_specialist_emergency", parameters)




def send_wa_payment_pending_reminder (to_phone, patient_name, salutation, specialist_name, datetime):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": datetime},
    ]

    
    return whatsapp_api_handler(to_phone, "payment_pending_reminder", parameters)



def send_wa__final_payment_reminder_24_hours_before_consultation_time(to_phone, patient_name, salutation, specialist_name, datetime):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": datetime},
    ]

    
    return whatsapp_api_handler(to_phone, "_final_payment_reminder_24_hours_before_consultation_time", parameters)




def send_wa_refund_processed(to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]

    
    return whatsapp_api_handler(to_phone, "refund_processed", parameters)




def send_wa_warning_regarding_inappropriate_behavior_patient(to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]

    
    return whatsapp_api_handler(to_phone, "warning_regarding_inappropriate_behavior_patient", parameters)



def send_wa_permanent_ban_notification_patient(to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]

    
    return whatsapp_api_handler(to_phone, "permanent_ban_notification_patient", parameters)






def send_wa_consultation_missed_specialist_noshow(to_phone, patient_name, specialist_name, date_time):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

      
    return whatsapp_api_handler(to_phone, "consultation_missed_specialist_noshow", parameters)


def send_wa_patient_chat_notification_to_specialist (to_phone, specialist_name):
    parameters = [
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]

      
    return whatsapp_api_handler(to_phone, "patient_chat_notification_to_specialist", parameters)


def send_wa_specialist_reply_notification_to_patient (to_phone , specialist_name):
    parameters = [
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]
      
    return whatsapp_api_handler(to_phone, "specialist_reply_notification_to_patient", parameters)
