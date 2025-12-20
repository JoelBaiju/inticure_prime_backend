import requests
import requests
from django.http import JsonResponse
from django.conf import settings



# def whatsapp_api_handler(
#    to_phone , template_name , parameters
# ):
#     """
#     Send WhatsApp template message using Meta's Graph API.
#     """
#     ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
#     PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID
    
#     url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to_phone if to_phone.startswith("+") else f"+{to_phone}",
#         "type": "template",
#         "template": {
#             "name": template_name,
#             "language": {"code": "en_US"},  # ✅ Use en_US for safety
#             "components": [
#                 {
#                     "type": "body",
#                     "parameters": parameters
#                 },

#                 # {
#                 #     "type": "button",
#                 #     "sub_type": "url",
#                 #     "index": 0,
#                 #     "parameters": [
#                 #     {
#                 #         "type": "text",
#                 #         "text": "https://yourdomain.com/verify?code=123456"
#                 #     }
#                 #         ]
#                 # }
#             ]}
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         return {
#             "error": str(e),
#             "response_text": getattr(response, "text", "No response")
#         }


















import logging
logger = logging.getLogger(__name__)







def whatsapp_api_handler(to_phone, template_name, body_parameters, button_parameters=None , language_code="en"):
    """
    Send WhatsApp template message using Meta's Graph API.
    """
    ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
    PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID
    logger.info("WA TOKEN DEBUG:")
    logger.error(f"WA TOKEN DEBUG: {repr(ACCESS_TOKEN)} | len={len(ACCESS_TOKEN) if ACCESS_TOKEN else 0}")

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    components = [
        {
            "type": "body",
            "parameters": body_parameters
        }
    ]
    
    if button_parameters:
        components.append({
            "type": "button",
            "sub_type": "url",
            "index": "0",  
            "parameters": button_parameters
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone if to_phone.startswith("+") else f"+{to_phone}",
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},  # Use specified language code
            "components": components
        }
    }
    logger.info("before trying ")
    logger.info(payload)
    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.info(response.json())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(str(e))
        return {
            "error": str(e),
            "response_text": getattr(response, "text", "No response") if 'response' in locals() else "No response"
        }