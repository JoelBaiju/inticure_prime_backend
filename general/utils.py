
import secrets
import string
from django.conf import settings


def generate_random_otp(length=6):
    otp=''.join(secrets.choice(string.digits) for _ in range(length))
    print(otp)
    return otp







from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

def send_otp_email(firstname,otp,toemail):
    subject = 'Your OTP for Email Verification'
    html_message = render_to_string('email_otp.html', {
    'name': firstname,
    'otp': otp
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
    subject,
    plain_message,
    settings.DEFAULT_FROM_EMAIL,  # Use the default from email
    [toemail]    
    )
    email.attach_alternative(html_message, 'text/html')
    print(f"Sending OTP email to {toemail}")
    print(email.send())
    
    



