import requests
import json
import requests
import json
import os
from django.http import JsonResponse
from django.conf import settings

def send_whatsapp_template_message():
    # Use environment variables for security
    ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
    PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID
    
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": "+917034761676",  # ✅ FIXED: Added + prefix
        "type": "template",
        "template": {
            "name": "patient_requested_cancellation",
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "Alex"},                # {{1}}
                        {"type": "text", "text": "Dr."},                 # {{2}}
                        {"type": "text", "text": "Smith"},               # {{3}}
                        {"type": "text", "text": "10 Sep 2025, 3:00 PM"} # {{4}}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)  # ✅ Use json= instead of data=
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "response_text": response.text if response else "No response"}

def test_send_whatsapp(request):
    result = send_whatsapp_template_message()
    return JsonResponse(result)