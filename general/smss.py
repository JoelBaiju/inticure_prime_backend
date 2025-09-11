from .twilio import send_sms
from analysis.models import AppointmentHeader

def appointmentbooked(appointment_id):

    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    message = "Your appointment has been booked successfully."
    
    # Format the start_time to display date and time separately
    appointment_date = appointment.start_time.date() if appointment.start_time else None
    appointment_time = appointment.start_time.time() if appointment.start_time else None
    
    body = f"Dear {appointment.customer.user.first_name},\n\n{message}\n\nAppointment Details:\nDate: {appointment_date}\nTime: {appointment_time}\nThank you for choosing our service!"

    send_sms(body, appointment.confirmation_phone_number)

    return "Your appointment has been booked successfully."