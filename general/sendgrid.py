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
    



from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_via_sendgrid(subject, html_content, to_email):
    """
    Generic SendGrid email sender.
    - subject: Email subject
    - html_content: Rendered HTML string
    - to_email: String or list of recipient email addresses
    """
    if isinstance(to_email, str):
        to_email = [to_email] 

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY) 
        response = sg.send(message)
        # print(settings.SENDGRID_API_KEY)
        print(f"Email sent to {to_email} | Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        # print(settings.SENDGRID_API_KEY)
        print(f"Error sending email to {to_email}: {e}")
        return None







from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def send_email_via_smtp(subject, html_content, to_email):
    """
    Generic SMTP email sender using Django's configured EmailBackend.
    - subject: Email subject
    - html_content: Rendered HTML string
    - to_email: String or list of recipient email addresses
    """
    if isinstance(to_email, str):
        to_email = [to_email]  # ensure list format

    # Plain text version for fallback (in case HTML is not supported)
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_email,
        )
        msg.attach_alternative(html_content, "text/html")  # Attach HTML version
        msg.send()

        print(f"Email sent to {to_email} | Backend: SMTP")
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False
