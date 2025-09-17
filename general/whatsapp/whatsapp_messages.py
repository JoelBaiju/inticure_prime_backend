from .api import whatsapp_api_handler



def send_wa_consultation_canceled_by_patient_to_specialist(to_phone, patient_name, specialist_name, date_time):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

        
    return whatsapp_api_handler(to_phone, "consultation_canceled_by_patient_to_specialist", parameters)



def send_wa_patient_requested_cancellation (to_phone, patient_name,salutation, specialist_name, date_time):
    
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "doctor_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
    ]

    
    return whatsapp_api_handler(to_phone, "patient_requested_cancellation", parameters)













def send_wa_appointment_confirmation(patient_name, salutation, specialist_name, date_time, meet_link, to_phone):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
        {"type": "text", "parameter_name": "meet_link", "text": meet_link},
    ]
    return whatsapp_api_handler(to_phone, "appointment_confirmation", parameters)





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




def send_wa_consultation_reminder_24_hours_before(to_phone, patient_name, salutation, specialist_name, date_time, meet_code):
    body_parameters = [
        {"type": "text", "text": patient_name, "parameter_name": "name"},
        {"type": "text", "text": salutation, "parameter_name": "salutation"},
        {"type": "text", "text": specialist_name, "parameter_name": "specialist_name"},
        {"type": "text", "text": date_time, "parameter_name": "date_time"},
    ]
    
    button_parameters = [
        {
            "type": "text", 
            "text": meet_code 
        }
    ]
    
    return whatsapp_api_handler(to_phone, "consultation_reminder_24_hours_before", body_parameters, button_parameters)















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




def send_wa_consultation_rescheduled_by_specialist(to_phone, patient_name, salutation, specialist_name, old_date_time, new_date_time):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]

    return whatsapp_api_handler(to_phone, "consultation_rescheduled_by_specialist", parameters)



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



def send_wa_welcome_to_inticure (to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]

    
    return whatsapp_api_handler(to_phone, "welcome_to_inticure", parameters)



def send_wa_first_consultation_confirmation(to_phone, patient_name, salutation, specialist_name, date_time, meet_code):
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


def send_wa_consultation_confirmation_to_specialist(to_phone, patient_name,  specialist_name, date_time, meet_code):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

      
    return whatsapp_api_handler(to_phone, "consultation_confirmation_to_specialist", parameters)


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

def send_wa_consultation_rescheduled_by_patient_to_specialist(to_phone, patient_name, specialist_name, old_date_time, new_date_time):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "old_datetime", "text": old_date_time},
        {"type": "text", "parameter_name": "new_datetime", "text": new_date_time},
    ]

        
    return whatsapp_api_handler(to_phone, "consultation_rescheduled_by_patient_to_specialist", parameters)
