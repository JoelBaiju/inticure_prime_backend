import os
import json


from decouple import config



def create_google_credentials_file(filename='google_credentials.json'):
    credentials = {
        "web": {
            "client_id": config("GOOGLE_CLIENT_ID"),
            "project_id": config("GOOGLE_PROJECT_ID"),
            "auth_uri": config("GOOGLE_AUTH_URI"),
            "token_uri": config("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": config("GOOGLE_AUTH_PROVIDER_CERT_URL"),
            "client_secret": config("GOOGLE_CLIENT_SECRET"),
        }
    }

    with open(filename, 'w') as f:
        json.dump(credentials, f)

    return filename
