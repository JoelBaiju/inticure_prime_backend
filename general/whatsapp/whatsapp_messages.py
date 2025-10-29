# from .api import whatsapp_api_handler
# from analysis.models import Appointment_customers, AppointmentHeader, Meeting_Tracker
# from ..utils import convert_datetime_to_words_in_local_tz
# from ..models import Reminder_Sent_History
# import logging
# logger = logging.getLogger(__name__)


# def send_wa_consultation_canceled_by_patient_to_specialist(appointment_id):

#     logger.debug("c send_wa_consultation_canceled_by_patient_to_specialist")
#     try:
#         appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name    = appointment.customer.user.first_name
#         specialist_name = appointment.doctor.first_name
#         date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.doctor.time_zone)     
#         to_phone        = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number
#     except AppointmentHeader.DoesNotExist:
#         print(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."

#     parameters = [
#         {"type": "text", "parameter_name": "patient_name", "text": patient_name},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "datetime", "text": date_time},
#     ]

        
#     return whatsapp_api_handler(to_phone, "consultation_canceled_by_patient_to_specialist", parameters)



# def send_wa_patient_requested_cancellation (appointment_id):
#     try:
#         appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name    = appointment.customer.user.first_name
#         specialist_name = appointment.doctor.first_name
#         salutation      = appointment.doctor.salutation
#         date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)
#         to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number

#     except AppointmentHeader.DoesNotExist:
#         print(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."    
#     parameters = [
#         {"type": "text", "parameter_name": "patient_name", "text": patient_name},
#         {"type": "text", "parameter_name": "salutation", "text": salutation},
#         {"type": "text", "parameter_name": "doctor_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "date_time", "text": date_time},
#     ]

    
#     return whatsapp_api_handler(to_phone, "patient_requested_cancellation", parameters)




# # ====================================================================================================================



# def send_wa_welcome_to_inticure (to_phone, patient_name):
#     parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#     ]

    
#     return whatsapp_api_handler(to_phone, "welcome_to_inticure", parameters)

# # ====================================================================================================================


# def send_wa_appointment_confirmation(appointment_id):
#     try:    
#         appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name    = appointment.customer.user.first_name
#         specialist_name = appointment.doctor.first_name
#         salutation      = appointment.doctor.salutation
#         date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)
#         meet_link       = Meeting_Tracker.objects.get(appointment=appointment).customer_1_meeting_link
#         # to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number
#         to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number
#         meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
#         meet_code       = meeting_tracker.customer_1_meeting_id
#         # country_code    = str(appointment.customer.country_code)
#     except AppointmentHeader.DoesNotExist:
#         print(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."

#     parameters = [
#         {"type": "text", "parameter_name": "patient_name", "text": patient_name},
#         {"type": "text", "parameter_name": "salutation", "text": salutation},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "date_time", "text": date_time},
#     ]

    
#     button_parameters = [
#         {
#             "type": "text", 
#             "text": str(meet_code) 
#         }
#     ]
#     # return whatsapp_api_handler(to_phone, "appointment_confirmation", parameters ,button_parameters)
#     return whatsapp_api_handler(to_phone, "appointment_confirmation_2", parameters ,button_parameters)






# def send_wa_first_consultation_confirmation(appointment_id):
#     try:
#         appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name    = appointment.customer.user.first_name
#         specialist_name = appointment.doctor.first_name
#         salutation      = appointment.doctor.salutation
#         date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)  
#         to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number

#         meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
#         meet_code       = meeting_tracker.customer_1_meeting_id

#     except AppointmentHeader.DoesNotExist:
#         print(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."

#     parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#         {"type": "text", "parameter_name": "salutation", "text": salutation},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "datetime", "text": date_time},
#     ]

#     button_parameters = [
#         {
#             "type": "text", 
#             "text": str(meet_code) 
#         }
#     ]
#     return whatsapp_api_handler(to_phone, "first_consultation_confirmation", parameters , button_parameters)




# def send_wa_consultation_confirmation_to_specialist(appointment_id):
#     try:
#         appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name    = appointment.customer.user.first_name
#         specialist_name = appointment.doctor.first_name
#         date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.doctor.time_zone)
#         to_phone        = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number


#     except AppointmentHeader.DoesNotExist:
#         print(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."

#     parameters = [
#         {"type": "text", "parameter_name": "patient_name", "text": patient_name},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "datetime", "text": date_time},
#     ]

      
#     return whatsapp_api_handler(to_phone, "consultation_confirmation_to_specialist", parameters)




# # ====================================================================================================================


# def send_wa_auth_code(to_phone, auth_code):
#     body_parameters = [
#         {"type": "text", "text": auth_code},
#     ]
#     button_parameters = [
#         {
#             "type": "text",
#             "text": auth_code 
#         }
#     ]
    
#     return whatsapp_api_handler(to_phone, "auth_otp", body_parameters, button_parameters , "en_US")


# # ======================================================================================================================




# def send_wa_consultation_rescheduled_by_specialist(appointment_id):

#     try:

        
                
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         specialist_name = appointment.doctor.first_name
#         salutation = appointment.doctor.salutation
#         appt_customers = Appointment_customers.objects.filter(appointment=appointment)
#         for customer in appt_customers:
#             patient_name =f"{customer.customer.user.first_name} {customer.customer.user.last_name}"

#             parameters = [
#                 {"type": "text", "parameter_name": "name", "text": patient_name},
#                 {"type": "text", "parameter_name": "salutation", "text": salutation},
#                 {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#             ]

#         logger.debug(whatsapp_api_handler(f"{customer.customer.country_code}{customer.customer.whatsapp_number}", "consultation_rescheduled_by_specialist", parameters))

#     except Exception as e:
#         logger.debug(f"Error in send_wa_consultation_rescheduled_by_specialist.for id {appointment_id}. Error {e}")
#         return f"Error in send_wa_consultation_rescheduled_by_specialist. {e}"



# def send_wa_consultation_rescheduled_by_patient_to_specialist(appointment_id ,  old_date_time, new_date_time):
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name = appointment.customer.user.first_name
#         specialist_name = appointment.doctor.first_name
#         to_phone = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number

#         parameters = [
#             {"type": "text", "parameter_name": "patient_name", "text": patient_name},
#             {"type": "text", "parameter_name": "specialist_name", "text":  specialist_name},
#             {"type": "text", "parameter_name": "old_datetime", "text": convert_datetime_to_words_in_local_tz(old_date_time , appointment.doctor.time_zone)},
#             {"type": "text", "parameter_name": "new_datetime", "text": convert_datetime_to_words_in_local_tz(new_date_time , appointment.doctor.time_zone)},
#         ]

            
#         return whatsapp_api_handler(to_phone, "consultation_rescheduled_by_patient_to_specialist", parameters)

#     except Exception as e:
#         logger.error("wa_consultation_rescheduled_by_patient_to_specialist error" , e)
#         return "Message not sent"


# # ======================================================================================================================


# def send_wa_consultation_reminder_24_hours_before(appointment_id):
#     """Send and track 24-hour consultation reminder via WhatsApp"""
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         specialist_name =f"{ appointment.doctor.first_name} { appointment.doctor.last_name}"
#         salutation = appointment.doctor.salutation
#         tracker = Meeting_Tracker.objects.get(appointment = appointment)
#         appt_customers = appointment.appointment_customers.all()
  

#         for customer in appt_customers:
#             meet_code = tracker.customer_1_meeting_id if customer.customer == tracker.customer_1 else tracker.customer_2_meeting_id
                
#             body_parameters = [
#                 {"type": "text", "text": f"{customer.customer.user.first_name} {customer.customer.user.last_name}", "parameter_name": "name"},
#                 {"type": "text", "text": salutation, "parameter_name": "salutation"},
#                 {"type": "text", "text": specialist_name, "parameter_name": "specialist_name"},
#                 {"type": "text", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , customer.customer.time_zone), "parameter_name": "date_time"},
#             ]
            
#             button_parameters = [
#                 {
#                     "type": "text", 
#                     "text": meet_code 
#                 }
#             ]
            
#             whatsapp_api_handler(f"{customer.customer.country_code}{customer.customer.whatsapp_number}", "consultation_reminder_24_hours_before", body_parameters, button_parameters)

#     except AppointmentHeader.DoesNotExist:
#         logger.error(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."
#     except Exception as e:
#         logger.error("wa_consultation_reminder 24 hours before error" , e)
#         return "Message not sent"





# def send_wa_consultation_reminder_1_hour_before (appointment_id): 
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         specialist_name =f"{ appointment.doctor.first_name} { appointment.doctor.last_name}"
#         salutation = appointment.doctor.salutation
#         tracker = Meeting_Tracker.objects.get(appointment = appointment)
#         appt_customers = appointment.appointment_customers.all()
#         for customer in appt_customers:
#             meet_code = tracker.customer_1_meeting_id if customer.customer == tracker.customer_1 else tracker.customer_2_meeting_id
#             parameters = [
#                 {"type": "text", "text": f"{customer.customer.user.first_name} {customer.customer.user.last_name}", "parameter_name": "patient_name"},
#                 {"type": "text", "text": salutation, "parameter_name": "salutation"},
#                 {"type": "text", "text": specialist_name, "parameter_name": "specialist_name"},
#                 {"type": "text", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , customer.customer.time_zone), "parameter_name": "time"},
#             ]
#             button_parameters = [
#                 {
#                     "type": "text", 
#                     "text": meet_code 
#                 }
#             ]
#             return whatsapp_api_handler(f"{customer.customer.country_code}{customer.customer.whatsapp_number}", "consultation_reminder_1_hour_before", parameters, button_parameters)

#     except AppointmentHeader.DoesNotExist:
#         logger.error(f"Appointment does not exist.for id {appointment_id}")
#         return "Appointment does not exist."
#     except Exception as e:
#         logger.error("wa_consultation_reminder 1 hour before error" , e)
#         return "Message not sent"

        


# def send_wa_specialist_reminder_1_hour_before(appointment_id):
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         specialist_name =f"{ appointment.doctor.first_name} { appointment.doctor.last_name}"
#         salutation = appointment.doctor.salutation
#         tracker = Meeting_Tracker.objects.get(appointment = appointment)
    
#         parameters = [
#             {"type": "text", "parameter_name": "patient_name", "text": f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"},
#             {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#             {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
#         ]

            
#         button_parameters = [
#             {
#                 "type": "text", 
#                 "text": tracker.doctor_meeting_id 
#             }
#         ]

#         return whatsapp_api_handler(f"{appointment.doctor.whatsapp_country_code}{appointment.doctor.whatsapp_number}", "specialist_reminder_1_hour_before", parameters, button_parameters)

#     except Exception as e:
#         logger.error("wa_specialist_reminder 1 hour before error" , e)
#         return "Message not sent"





# # ===================================================================================+===================================



# def send_wa_consultation_reminder_not_yet_scheduled(patient_name,salutation,specialist_name , to_phone):
#     try:
       
#         parameters = [
#             {"type": "text", "parameter_name": "name", "text": patient_name},
#             {"type": "text", "parameter_name": "salutation", "text": salutation},
#             {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         ]
    

    
#         return whatsapp_api_handler( to_phone, "consultation_reminder_not_yet_scheduled", parameters)
#     except Exception as e:
#         logger.error("wa_consultation_reminder not yet scheduled error" , e)
#         return "Message not sent"


# def send_wa_final_consultation_reminder_not_yet_scheduled(patient_name,salutation,specialist_name , to_phone):
#     try:
      
#         parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#         {"type": "text", "parameter_name": "salutation", "text": salutation},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         ]

        
#         return whatsapp_api_handler(to_phone, "final_consultation_reminder_not_yet_scheduled", parameters)
#     except Exception as e:
#         logger.error("wa_final_consultation_reminder not yet scheduled error" , e)
#         return "Message not sent"


# # patient missed
# def send_wa_missed_consultation_patient_did_not_join(appointment_id):
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
#         salutation = appointment.doctor.salutation
#         specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
#         parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#         {"type": "text", "parameter_name": "salutation", "text": salutation},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
#         ]

    
#         return whatsapp_api_handler(f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}", "missed_consultation_patient_did_not_join", parameters)
#     except Exception as e:
#         logger.error("wa_missed_consultation_patient_did_not_join error" , e)
#         return "Message not sent"


# # doctor missed
# def send_wa_consultation_interrupted_specialist_emergency(appointment_id):
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
#         salutation = appointment.doctor.salutation
#         specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
#         parameters = [
#             {"type": "text", "parameter_name": "name", "text": patient_name},
#             {"type": "text", "parameter_name": "salutation", "text": salutation},
#             {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#             {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
#         ]
#         return whatsapp_api_handler(f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}", "consultation_interrupted_specialist_emergency", parameters)
#     except Exception as e:
#         logger.error("wa_consultation_interrupted_specialist_emergency error" , e)
#         return "Message not sent"




# def send_wa_payment_pending_reminder(appointment_id):
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
#         salutation = appointment.doctor.salutation
#         specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
#         parameters = [
#             {"type": "text", "parameter_name": "name", "text": patient_name},
#             {"type": "text", "parameter_name": "salutation", "text": salutation},
#             {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#             {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
#         ]
#         return whatsapp_api_handler(f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}", "payment_pending_reminder", parameters)
#     except Exception as e:
#         logger.error("wa_payment_pending_reminder error" , e)
#         return "Message not sent"

# def send_wa__final_payment_reminder_24_hours_before_consultation_time(appointment_id):
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
#         salutation = appointment.doctor.salutation
#         specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
#         parameters = [
#             {"type": "text", "parameter_name": "name", "text": patient_name},
#             {"type": "text", "parameter_name": "salutation", "text": salutation},
#             {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#             {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
#         ]
#         return whatsapp_api_handler(f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}", "_final_payment_reminder_24_hours_before_consultation_time", parameters)
#     except Exception as e:
#         logger.error("wa__final_payment_reminder_24_hours_before_consultation_time error" , e)
#         return "Message not sent"









# def send_wa_refund_processed(to_phone, patient_name):
#     parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#     ]

    
#     return whatsapp_api_handler(to_phone, "refund_processed", parameters)




# def send_wa_warning_regarding_inappropriate_behavior_patient(to_phone, patient_name):
#     parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#     ]

    
#     return whatsapp_api_handler(to_phone, "warning_regarding_inappropriate_behavior_patient", parameters)



# def send_wa_permanent_ban_notification_patient(to_phone, patient_name):
#     parameters = [
#         {"type": "text", "parameter_name": "name", "text": patient_name},
#     ]

    
#     return whatsapp_api_handler(to_phone, "permanent_ban_notification_patient", parameters)






# def send_wa_consultation_missed_specialist_noshow(to_phone, patient_name, specialist_name, date_time):
#     parameters = [
#         {"type": "text", "parameter_name": "patient_name", "text": patient_name},
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "datetime", "text": date_time},
#     ]

      
#     return whatsapp_api_handler(to_phone, "consultation_missed_specialist_noshow", parameters)


# def send_wa_patient_chat_notification_to_specialist (to_phone, specialist_name):
#     parameters = [
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#     ]

      
#     return whatsapp_api_handler(to_phone, "patient_chat_notification_to_specialist", parameters)


# def send_wa_specialist_reply_notification_to_patient (to_phone ,name, specialist_name):
#     parameters = [
#         {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         {"type": "text", "parameter_name": "name", "text": name},
#     ]
      
#     return whatsapp_api_handler(to_phone, "specialist_reply_notification_to_patient", parameters)

# def track_whatsapp_reminder(user, appointment, whatsapp_number, template_name, parameters, user_is_customer=False):
#     """Helper function to track whatsapp reminders"""
#     # Construct body from parameters
#     body = f"Template: {template_name}, Parameters: {str(parameters)}"
#     Reminder_Sent_History.objects.create(
#         user=user,
#         user_is_customer=user_is_customer,
#         appointment=appointment,
#         whatsapp_number=whatsapp_number,
#         email="",  # Not used for WhatsApp reminders
#         subject=template_name,
#         body=body
#     )

















































from .api import whatsapp_api_handler
from analysis.models import Appointment_customers, AppointmentHeader, Meeting_Tracker
from ..utils import convert_datetime_to_words_in_local_tz
from ..models import Reminder_Sent_History
import logging
logger = logging.getLogger(__name__)


def send_wa_consultation_canceled_by_patient_to_specialist(appointment_id):

    logger.debug("c send_wa_consultation_canceled_by_patient_to_specialist")
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.doctor.time_zone)
        to_phone        = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number
    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]

    # send and track
    return send_and_track(
        to_phone=to_phone,
        template_name="consultation_canceled_by_patient_to_specialist",
        parameters=parameters,
        button_parameters=None,
        user=appointment.doctor,
        appointment=appointment,
        user_is_customer=False
    )


def send_wa_patient_requested_cancellation (appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        salutation      = appointment.doctor.salutation
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)
        to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "doctor_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
    ]

    return send_and_track(
        to_phone=to_phone,
        template_name="patient_requested_cancellation",
        parameters=parameters,
        button_parameters=None,
        user=appointment.customer.user,
        appointment=appointment,
        user_is_customer=True
    )




# ====================================================================================================================



def send_wa_welcome_to_inticure (to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]

    # No appointment / user available here — track with user=None
    return send_and_track(
        to_phone=to_phone,
        template_name="welcome_to_inticure",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=True
    )

# ====================================================================================================================


def send_wa_appointment_confirmation(appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        salutation      = appointment.doctor.salutation
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)
        # to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number
        to_phone        = appointment.customer.country_code + appointment.customer.whatsapp_number
        meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
        meet_code       = meeting_tracker.customer_1_meeting_id
    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_time", "text": date_time},
    ]

    button_parameters = [
        {
            "type": "text",
            "text": str(meet_code)
        }
    ]
    # return whatsapp_api_handler(to_phone, "appointment_confirmation", parameters ,button_parameters)
    return send_and_track(
        to_phone=to_phone,
        template_name="appointment_confirmation_2",
        parameters=parameters,
        button_parameters=button_parameters,
        user=appointment.customer.user,
        appointment=appointment,
        user_is_customer=True
    )






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
        logger.error(f"Appointment does not exist.for id {appointment_id}")
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
            "text": str(meet_code)
        }
    ]
    return send_and_track(
        to_phone=to_phone,
        template_name="first_consultation_confirmation",
        parameters=parameters,
        button_parameters=button_parameters,
        user=appointment.customer.user,
        appointment=appointment,
        user_is_customer=True
    )




def send_wa_consultation_confirmation_to_specialist(appointment_id):
    try:
        appointment     = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name    = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        date_time       = convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.doctor.time_zone)
        to_phone        = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number


    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."

    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]


    return send_and_track(
        to_phone=to_phone,
        template_name="consultation_confirmation_to_specialist",
        parameters=parameters,
        button_parameters=None,
        user=appointment.doctor.user,
        appointment=appointment,
        user_is_customer=False
    )




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

    return send_and_track(
        to_phone=to_phone,
        template_name="auth_otp",
        parameters=body_parameters,
        button_parameters=button_parameters,
        user=None,
        appointment=None,
        user_is_customer=True,
        locale="en_US"
    )


# ======================================================================================================================




def send_wa_consultation_rescheduled_by_specialist(appointment_id):

    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        specialist_name = appointment.doctor.first_name
        salutation = appointment.doctor.salutation
        appt_customers = Appointment_customers.objects.filter(appointment=appointment)

        results = []
        for customer in appt_customers:
            patient_name = f"{customer.customer.user.first_name} {customer.customer.user.last_name}"

            parameters = [
                {"type": "text", "parameter_name": "name", "text": patient_name},
                {"type": "text", "parameter_name": "salutation", "text": salutation},
                {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
            ]

            to_phone = f"{customer.customer.country_code}{customer.customer.whatsapp_number}"
            res = send_and_track(
                to_phone=to_phone,
                template_name="consultation_rescheduled_by_specialist",
                parameters=parameters,
                button_parameters=None,
                user=customer.customer.user,
                appointment=appointment,
                user_is_customer=True
            )
            results.append(res)

        logger.debug(f"send_wa_consultation_rescheduled_by_specialist results: {results}")
        return results

    except Exception as e:
        logger.debug(f"Error in send_wa_consultation_rescheduled_by_specialist.for id {appointment_id}. Error {e}")
        return f"Error in send_wa_consultation_rescheduled_by_specialist. {e}"



def send_wa_consultation_rescheduled_by_patient_to_specialist(appointment_id ,  old_date_time, new_date_time):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name = appointment.customer.user.first_name
        specialist_name = appointment.doctor.first_name
        to_phone = appointment.doctor.whatsapp_country_code + appointment.doctor.whatsapp_number

        parameters = [
            {"type": "text", "parameter_name": "patient_name", "text": patient_name},
            {"type": "text", "parameter_name": "specialist_name", "text":  specialist_name},
            {"type": "text", "parameter_name": "old_datetime", "text": convert_datetime_to_words_in_local_tz(old_date_time , appointment.doctor.time_zone)},
            {"type": "text", "parameter_name": "new_datetime", "text": convert_datetime_to_words_in_local_tz(new_date_time , appointment.doctor.time_zone)},
        ]


        return send_and_track(
            to_phone=to_phone,
            template_name="consultation_rescheduled_by_patient_to_specialist",
            parameters=parameters,
            button_parameters=None,
            user=appointment.doctor.user,
            appointment=appointment,
            user_is_customer=False
        )

    except Exception as e:
        logger.error("wa_consultation_rescheduled_by_patient_to_specialist error" , e)
        return "Message not sent"


# ======================================================================================================================


def send_wa_consultation_reminder_24_hours_before(appointment_id):
    """Send and track 24-hour consultation reminder via WhatsApp"""
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        specialist_name = f"{ appointment.doctor.first_name} { appointment.doctor.last_name}"
        salutation = appointment.doctor.salutation
        tracker = Meeting_Tracker.objects.get(appointment = appointment)
        appt_customers = appointment.appointment_customers.all()

        results = []
        for customer in appt_customers:
            meet_code = tracker.customer_1_meeting_id if customer.customer == tracker.customer_1 else tracker.customer_2_meeting_id

            body_parameters = [
                {"type": "text", "text": f"{customer.customer.user.first_name} {customer.customer.user.last_name}", "parameter_name": "name"},
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

            to_phone = f"{customer.customer.country_code}{customer.customer.whatsapp_number}"
            res = send_and_track(
                to_phone=to_phone,
                template_name="consultation_reminder_24_hours_before",
                parameters=body_parameters,
                button_parameters=button_parameters,
                user=customer.customer.user,
                appointment=appointment,
                user_is_customer=True
            )
            results.append(res)

        return results

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.error("wa_consultation_reminder 24 hours before error" , e)
        return "Message not sent"





def send_wa_consultation_reminder_1_hour_before (appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        specialist_name = f"{ appointment.doctor.first_name} { appointment.doctor.last_name}"
        salutation = appointment.doctor.salutation
        tracker = Meeting_Tracker.objects.get(appointment = appointment)
        appt_customers = appointment.appointment_customers.all()

        results = []
        for customer in appt_customers:
            meet_code = tracker.customer_1_meeting_id if customer.customer == tracker.customer_1 else tracker.customer_2_meeting_id
            parameters = [
                {"type": "text", "text": f"{customer.customer.user.first_name} {customer.customer.user.last_name}", "parameter_name": "patient_name"},
                {"type": "text", "text": salutation, "parameter_name": "salutation"},
                {"type": "text", "text": specialist_name, "parameter_name": "specialist_name"},
                {"type": "text", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , customer.customer.time_zone), "parameter_name": "time"},
            ]
            button_parameters = [
                {
                    "type": "text",
                    "text": meet_code
                }
            ]
            to_phone = f"{customer.customer.country_code}{customer.customer.whatsapp_number}"
            res = send_and_track(
                to_phone=to_phone,
                template_name="consultation_reminder_1_hour_before",
                parameters=parameters,
                button_parameters=button_parameters,
                user=customer.customer.user,
                appointment=appointment,
                user_is_customer=True
            )
            results.append(res)

        return results

    except AppointmentHeader.DoesNotExist:
        logger.error(f"Appointment does not exist.for id {appointment_id}")
        return "Appointment does not exist."
    except Exception as e:
        logger.error("wa_consultation_reminder 1 hour before error" , e)
        return "Message not sent"




def send_wa_specialist_reminder_1_hour_before(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        specialist_name = f"{ appointment.doctor.first_name} { appointment.doctor.last_name}"
        salutation = appointment.doctor.salutation
        tracker = Meeting_Tracker.objects.get(appointment = appointment)

        parameters = [
            {"type": "text", "parameter_name": "patient_name", "text": f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"},
            {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
            {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
        ]


        button_parameters = [
            {
                "type": "text",
                "text": tracker.doctor_meeting_id
            }
        ]

        to_phone = f"{appointment.doctor.whatsapp_country_code}{appointment.doctor.whatsapp_number}"
        return send_and_track(
            to_phone=to_phone,
            template_name="specialist_reminder_1_hour_before",
            parameters=parameters,
            button_parameters=button_parameters,
            user=appointment.doctor.user,
            appointment=appointment,
            user_is_customer=False
        )

    except Exception as e:
        logger.error("wa_specialist_reminder 1 hour before error" , e)
        return "Message not sent"





# ===================================================================================+===================================



# def send_wa_consultation_reminder_not_yet_scheduled(patient_name,salutation,specialist_name , to_phone):
#     try:

#         parameters = [
#             {"type": "text", "parameter_name": "name", "text": patient_name},
#             {"type": "text", "parameter_name": "salutation", "text": salutation},
#             {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
#         ]


#         return send_and_track(
#             to_phone=to_phone,
#             template_name="consultation_reminder_not_yet_scheduled",
#             parameters=parameters,
#             button_parameters=None,
#             user=None,
#             appointment=None,
#             user_is_customer=True
#         )
#     except Exception as e:
#         logger.error("wa_consultation_reminder not yet scheduled error" , e)
#         return "Message not sent"


def send_wa_consultation_reminder_not_yet_scheduled(appointment):
    try:
        patient_name=f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}",
        salutation=appointment.doctor.salutation,
        specialist_name=f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
        to_phone=f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
                    
        parameters = [
            {"type": "text", "parameter_name": "name", "text": patient_name},
            {"type": "text", "parameter_name": "salutation", "text": salutation},
            {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        ]


        return send_and_track(
            to_phone=to_phone,
            template_name="consultation_reminder_not_yet_scheduled",
            parameters=parameters,
            button_parameters=None,
            user=appointment.customer.user,
            appointment=appointment,
            user_is_customer=True
        )
    except Exception as e:
        logger.error("wa_consultation_reminder not yet scheduled error" , e)
        return "Message not sent"




def send_wa_final_consultation_reminder_not_yet_scheduled(patient_name,salutation,specialist_name , to_phone):
    try:

        parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        ]


        return send_and_track(
            to_phone=to_phone,
            template_name="final_consultation_reminder_not_yet_scheduled",
            parameters=parameters,
            button_parameters=None,
            user=None,
            appointment=None,
            user_is_customer=True
        )
    except Exception as e:
        logger.error("wa_final_consultation_reminder not yet scheduled error" , e)
        return "Message not sent"


# patient missed
def send_wa_missed_consultation_patient_did_not_join(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
        salutation = appointment.doctor.salutation
        specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
        parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
        {"type": "text", "parameter_name": "salutation", "text": salutation},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
        ]


        to_phone = f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
        return send_and_track(
            to_phone=to_phone,
            template_name="missed_consultation_patient_did_not_join",
            parameters=parameters,
            button_parameters=None,
            user=appointment.customer.user,
            appointment=appointment,
            user_is_customer=True
        )
    except Exception as e:
        logger.error("wa_missed_consultation_patient_did_not_join error" , e)
        return "Message not sent"


# doctor missed
def send_wa_consultation_interrupted_specialist_emergency(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
        salutation = appointment.doctor.salutation
        specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
        parameters = [
            {"type": "text", "parameter_name": "name", "text": patient_name},
            {"type": "text", "parameter_name": "salutation", "text": salutation},
            {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
            {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
        ]
        to_phone = f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
        return send_and_track(
            to_phone=to_phone,
            template_name="consultation_interrupted_specialist_emergency",
            parameters=parameters,
            button_parameters=None,
            user=appointment.customer.user,
            appointment=appointment,
            user_is_customer=True
        )
    except Exception as e:
        logger.error("wa_consultation_interrupted_specialist_emergency error" , e)
        return "Message not sent"




def send_wa_payment_pending_reminder(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
        salutation = appointment.doctor.salutation
        specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
        parameters = [
            {"type": "text", "parameter_name": "name", "text": patient_name},
            {"type": "text", "parameter_name": "salutation", "text": salutation},
            {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
            {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
        ]
        to_phone = f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
        return send_and_track(
            to_phone=to_phone,
            template_name="payment_pending_reminder",
            parameters=parameters,
            button_parameters=None,
            user=appointment.customer.user,
            appointment=appointment,
            user_is_customer=True
        )
    except Exception as e:
        logger.error("wa_payment_pending_reminder error" , e)
        return "Message not sent"

def send_wa__final_payment_reminder_24_hours_before_consultation_time(appointment_id):
    try:
        appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
        patient_name = f"{appointment.customer.user.first_name} {appointment.customer.user.last_name}"
        salutation = appointment.doctor.salutation
        specialist_name = f"{appointment.doctor.first_name} {appointment.doctor.last_name}"
        parameters = [
            {"type": "text", "parameter_name": "name", "text": patient_name},
            {"type": "text", "parameter_name": "salutation", "text": salutation},
            {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
            {"type": "text", "parameter_name": "datetime", "text": convert_datetime_to_words_in_local_tz(appointment.start_time , appointment.customer.time_zone)},
        ]
        to_phone = f"{appointment.customer.country_code}{appointment.customer.whatsapp_number}"
        return send_and_track(
            to_phone=to_phone,
            template_name="_final_payment_reminder_24_hours_before_consultation_time",
            parameters=parameters,
            button_parameters=None,
            user=appointment.customer.user,
            appointment=appointment,
            user_is_customer=True
        )
    except Exception as e:
        logger.error("wa__final_payment_reminder_24_hours_before_consultation_time error" , e)
        return "Message not sent"




def send_wa_refund_processed(to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]


    return send_and_track(
        to_phone=to_phone,
        template_name="refund_processed",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=True
    )




def send_wa_warning_regarding_inappropriate_behavior_patient(to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]


    return send_and_track(
        to_phone=to_phone,
        template_name="warning_regarding_inappropriate_behavior_patient",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=True
    )



def send_wa_permanent_ban_notification_patient(to_phone, patient_name):
    parameters = [
        {"type": "text", "parameter_name": "name", "text": patient_name},
    ]


    return send_and_track(
        to_phone=to_phone,
        template_name="permanent_ban_notification_patient",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=True
    )






def send_wa_consultation_missed_specialist_noshow(to_phone, patient_name, specialist_name, date_time):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "datetime", "text": date_time},
    ]


    return send_and_track(
        to_phone=to_phone,
        template_name="consultation_missed_specialist_noshow",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=False
    )


def send_wa_patient_chat_notification_to_specialist (to_phone, specialist_name):
    parameters = [
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
    ]


    return send_and_track(
        to_phone=to_phone,
        template_name="patient_chat_notification_to_specialist",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=False
    )


def send_wa_specialist_reply_notification_to_patient (to_phone ,name, specialist_name):
    parameters = [
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "name", "text": name},
    ]

    return send_and_track(
        to_phone=to_phone,
        template_name="specialist_reply_notification_to_patient",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=True
    )

def track_whatsapp_reminder(user, appointment, whatsapp_number, template_name, parameters, button_parameters, user_is_customer=False):
    """Helper function to track whatsapp reminders"""
    # Construct body from parameters
    body = f"Template: {template_name}, Parameters: {str(parameters)} , Button Parameters: {str(button_parameters)}"
    Reminder_Sent_History.objects.create(
        user=user,
        user_is_customer=user_is_customer,
        appointment=appointment,
        whatsapp_number=whatsapp_number,
        email="",  # Not u sed for WhatsApp reminders
        subject=template_name,
        body=body
    )







# for admin notification ======================================================





def send_wa_consultation_rescheduled_admin_notification(to_phone, initiated_by, doctor_name, username, appointment_id, prev_date_ist, prev_time_ist, prev_date_local, prev_time_local, new_date_ist, new_time_ist, new_date_local, new_time_local, patient_timezone):
    parameters = [  
        {"type": "text", "parameter_name": "initiated_by", "text": initiated_by},
        {"type": "text", "parameter_name": "doctor_name", "text": doctor_name},
        {"type": "text", "parameter_name": "username", "text": username},
        {"type": "text", "parameter_name": "appointment_id", "text": appointment_id},
        {"type": "text", "parameter_name": "prev_date_ist", "text": prev_date_ist},
        {"type": "text", "parameter_name": "prev_time_ist", "text": prev_time_ist},
        {"type": "text", "parameter_name": "prev_date_local", "text": prev_date_local},
        {"type": "text", "parameter_name": "prev_time_local", "text": prev_time_local},
        {"type": "text", "parameter_name": "new_date_ist", "text": new_date_ist},
        {"type": "text", "parameter_name": "new_time_ist", "text": new_time_ist},
        {"type": "text", "parameter_name": "new_date_local", "text": new_date_local},
        {"type": "text", "parameter_name": "new_time_local", "text": new_time_local},
        {"type": "text", "parameter_name": "patient_timezone", "text": patient_timezone},
    ]
    return send_and_track(
        to_phone=to_phone,
        template_name="appointment_rescheduled_admin",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=False
    )


def send_wa_consultation_confirmation_to_admin(to_phone, patient_name, specialist_name, date_time_ist , date_time_patient_tz , appointment_id ,patient_timezone):
    parameters = [
        {"type": "text", "parameter_name": "patient_name", "text": patient_name},
        {"type": "text", "parameter_name": "specialist_name", "text": specialist_name},
        {"type": "text", "parameter_name": "date_ist", "text": date_time_ist.date()}, 
        {"type": "text", "parameter_name": "time_ist", "text": date_time_ist.time()}, 
        {"type": "text", "parameter_name": "patient_timezone", "text": patient_timezone},
        {"type": "text", "parameter_name": "date_local", "text": date_time_patient_tz.date()}, 
        {"type": "text", "parameter_name": "time_local", "text": date_time_patient_tz.time()},
    ]

    return send_and_track(
        to_phone=to_phone,
        template_name="consultation_missed_specialist_noshow",
        parameters=parameters,
        button_parameters=None,
        user=None,
        appointment=None,
        user_is_customer=False
    )

# -------------------------------------------------------------------------
# Helper: centralised send + track (keeps parameter/template names unchanged)
# -------------------------------------------------------------------------
def send_and_track(to_phone, template_name, parameters, button_parameters=None, user=None, appointment=None, user_is_customer=False, locale=None):
    """
    Central helper to call whatsapp_api_handler and then track the reminder.
    - to_phone: full phone string (country code + number)
    - template_name: name of the template (unchanged)
    - parameters: list of parameter dicts (unchanged)
    - button_parameters: optional list for buttons (unchanged)
    - user: user object if available (can be None)
    - appointment: appointment object if available (can be None)
    - user_is_customer: boolean flag for tracking
    - locale: optional locale to pass to whatsapp_api_handler (e.g. "en_US")
    """
    try:
        if locale:
            response = whatsapp_api_handler(to_phone, template_name, parameters, button_parameters, locale)
        else:
            response = whatsapp_api_handler(to_phone, template_name, parameters, button_parameters)

        # Track the sent reminder for records
        try:
            track_whatsapp_reminder(
                user=user,
                appointment=appointment,
                whatsapp_number=to_phone,
                template_name=template_name,
                parameters=parameters,
                button_parameters=button_parameters,
                user_is_customer=user_is_customer
            )
        except Exception as track_exc:
            # Tracking should not break sending; log but continue
            logger.exception(f"Failed to track whatsapp reminder. template={template_name} to={to_phone} error={track_exc}")

        return response

    except Exception as e:
        logger.exception(f"Error sending whatsapp template {template_name} to {to_phone}: {e}")
        return None














