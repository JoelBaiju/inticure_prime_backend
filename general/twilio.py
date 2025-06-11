import json
import logging
import os

# from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
# from dotenv import load_dotenv
from twilio.rest import Client

from inticure_prime_backend import settings

logger = logging.getLogger(__name__)

# dotenv_path = settings.PROJECT_PATH / '.env'
# logger.debug(f'Reading .env file at: {dotenv_path}')
# load_dotenv(dotenv_path=dotenv_path)


MESSAGE = """[This is a test] ALERT! It appears the server is having issues.
Exception: {0}"""

NOT_CONFIGURED_MESSAGE = (
    "Required enviroment variables "
    "TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN or TWILIO_NUMBER missing."
)


# def load_admins_file():
#     admins_json_path = settings.PROJECT_PATH / 'config' / 'administrators.json'
#     logger.debug(f'Loading administrators info from: {admins_json_path}')
#     return json.loads(admins_json_path.read_text())


def load_twilio_config():
    logger.debug('Loading Twilio configuration')

    # twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    # twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_NUMBER')
    twilio_account_sid = settings.TWILIO_ACCOUNT_SID
    twilio_auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_number = settings.TWILIO_NUMBER
    # twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

    if not all([twilio_account_sid, twilio_auth_token, twilio_number, ]):
        raise ImproperlyConfigured(NOT_CONFIGURED_MESSAGE)

    return (twilio_number, twilio_account_sid, twilio_auth_token)


class MessageClient:
    def __init__(self):
        logger.debug('Initializing messaging client')

        (
            twilio_number,
            twilio_account_sid,
            twilio_auth_token,
        ) = load_twilio_config()

        # self.twilio_whatsapp_number = twilio_whatsapp_number
        self.twilio_number = twilio_number
        self.twilio_client = Client(twilio_account_sid, twilio_auth_token)

        logger.debug('Twilio client initialized')

    def send_message(self, body, to):
        response=self.twilio_client.messages.create(
            body=body,
            to=to,
            from_=self.twilio_number,
            # media_url=['https://demo.twilio.com/owl.png']
        )

        return response
    def send_messaging_service(self, body, to):
        self.twilio_client.messages.create(
            body=body,
            to=to,
            messaging_service_sid='MG7ca1f73aa7a581d1ed3d1a93ae791e84'
            # media_url=['https://demo.twilio.com/owl.png']
        )

    # def send_whatsapp_messaging(self, body, to,media_url):
    #     print(media_url)
    #     self.twilio_client.messages.create(
    #         from_='whatsapp:{}'.format(self.twilio_whatsapp_number),
    #         body=body,
    #         media_url=media_url,
    #         to='whatsapp:{}'.format(to),
    #         # messaging_service_sid='MG7ca1f73aa7a581d1ed3d1a93ae791e84'
    #         # media_url=['https://demo.twilio.com/owl.png']
    #     )


class TwilioNotificationsMiddleware:
    def __init__(self, get_response):
        logger.debug('Initializing Twilio notifications middleware')
        phone_json = [
            {
                "phone_number": "+15556667777",
                "name": "Foo Bar"
            }
        ]
        # self.administrators = load_admins_file()
        self.administrators = phone_json
        self.client = MessageClient()
        self.get_response = get_response

        logger.debug('Twilio notifications middleware initialized')

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        message_to_send = MESSAGE.format(exception)

        for admin in self.administrators:
            self.client.send_message(message_to_send, admin['phone_number'])

        logger.info('Administrators notified!')
        return None
    











def send_otp_sms(otp, to_number):

    client = MessageClient()
    body = f"Your Inticure verification code is: {otp}"
    try:
        response = client.send_message(body, to_number)

        print(response.status)
        
        print(f"OTP sent successfully to {to_number}")
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        raise

def send_sms(body, to_number):
    client = MessageClient()
    try:
        response = client.send_message(body, to_number)
        print(response.status)
        print(f"SMS sent successfully to {to_number}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        raise   