from .api import whatsapp_api_handler



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
    parameters = [
        {"type": "text", "text": auth_code},
    ]
    return whatsapp_api_handler(to_phone, "auth_otp", parameters)


def send_wa_patient_requested_cancellation (to_phone, patient_name,salutation, specialist_name, date_time):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "doctor_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
    ]
    return whatsapp_api_handler(to_phone, "patient_requested_cancellation", parameters)


def send_wa_consultation_reminder_24_hours_before (to_phone, patient_name,salutation, specialist_name, date_time, meet_code):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
        {"type": "button",  "text": meet_code},
    ]
    return whatsapp_api_handler(to_phone, "consultation_reminder_24_hours_before", parameters)


