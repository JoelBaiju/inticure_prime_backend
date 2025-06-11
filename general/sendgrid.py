import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings

sg = sendgrid.SendGridAPIClient(api_key=settings.EMAIL_HOST_PASSWORD)  # Use SendGrid API key from settings')
def send_mail(body, to_email):
    """
    Function to send an email using SendGrid.
    """
    email = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,  # Use the default from email
        to_emails=to_email,
        subject='Notification',
        html_content=body
    )
    
    try:
        response = sg.send(email)
        return response
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        return None
