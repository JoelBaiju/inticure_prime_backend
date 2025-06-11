from .twilio import send_sms


def appointmentbooked(appointment):


    message = "Your appointment has been booked successfully."
    
    body = f"Dear {appointment.customer.user.first_name},\n\n{message}\n\nAppointment Details:\nDate: {appointment['appointment_date']}\nTime: {appointment['appointment_time']}\nThank you for choosing our service!"

    send_sms(body, appointment.confirmation_phone_number)

    return "Your appointment has been booked successfully."