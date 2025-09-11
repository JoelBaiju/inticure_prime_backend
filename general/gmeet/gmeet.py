from __future__ import print_function
import os.path
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import httplib2
from google_auth_httplib2 import AuthorizedHttp






def normalize_meeting_code(meet_code: str) -> str:
    """
    Convert a Google Meet link-style code (e.g., 'mbq-xxhr-xxo')
    into the Reports API format (e.g., 'MBQXXHRXXO').

    Also works if the input is a full URL.
    """
    # If it's a URL, get only the part after the last slash
    if meet_code.startswith("http"):
        meet_code = meet_code.split("/")[-1]

    # Remove any spaces/whitespace
    meet_code = meet_code.strip()

    # Remove dashes and make uppercase
    return meet_code.replace("-", "").upper()



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).resolve().parent.parent

def generate_google_meet(summary, description, start_time, end_time):
    print("generate meet link functtion")
    try:
        print("meeting link try block")
        creds = None
        if os.path.exists(str(os.path.join(BASE_DIR, 'gmeet/token.json'))):
            creds = Credentials.from_authorized_user_file(str(os.path.join(BASE_DIR, 'gmeet/token.json')), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(os.path.join(BASE_DIR, 'gmeet/client_secret.json')),
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(str(os.path.join(BASE_DIR, 'gmeet/token.json')), 'w') as token:
                token.write(creds.to_json())
    except Exception as e:
        print("exception meeting link", e)
        return 0

    try:
        if isinstance(start_time, datetime):
            start_time = start_time.isoformat()
        if isinstance(end_time, datetime):
            end_time = end_time.isoformat()

        service = build('calendar', 'v3', credentials=creds)
        event_body = {
            "conferenceDataVersion": 1,
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },
                    "requestId": "RandomString",
                }
            },
            'visibility': 'public',
            "anyoneCanAddSelf": True,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(
            calendarId='primary',
            conferenceDataVersion=1,
            body=event_body
        ).execute()

        meeting_link = event.get('hangoutLink')
        meeting_code = None

        # Try to extract meeting code from conferenceData
        if 'conferenceData' in event and 'conferenceId' in event['conferenceData']:
            meeting_code = event['conferenceData']['conferenceId']
        elif meeting_link:
            # Fallback: parse from URL
            meeting_code = meeting_link.split('/')[-1]

        return {
            "meeting_link": meeting_link,
            "meeting_code": normalize_meeting_code(meeting_code)
        }

    except HttpError as error:
        print('An error occurred: %s' % error)
        return False












# Your super admin email
DELEGATED_ADMIN = 'nextbighealthcare@inticure.com'

# Scopes for Reports API (read-only Meet logs)
SCOPES2 = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust if needed
SERVICE_ACCOUNT_FILE = BASE_DIR  / 'gmeet' / 'inticure-382312-bd3b5ca5916f.json'








def fetch_meet_logs():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES2
    )
    delegated_credentials = credentials.with_subject(DELEGATED_ADMIN)

    # Create custom HTTP client with timeout
    http = httplib2.Http(timeout=300)
    authed_http = AuthorizedHttp(delegated_credentials, http=http)

    service = build('admin', 'reports_v1', http=authed_http)

    start_time = (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"

    results = service.activities().list(
        userKey='all',
        applicationName='meet',
        maxResults=10,
        # startTime=start_time
    ).execute()

    return results.get('items', [])




def fetch_meet_logs_with_meeting_code(meeting_code=None):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES2
    )
    delegated_credentials = credentials.with_subject(DELEGATED_ADMIN)

    # Create HTTP client with extended timeout
    http = httplib2.Http(timeout=300)
    authed_http = AuthorizedHttp(delegated_credentials, http=http)

    service = build('admin', 'reports_v1', http=authed_http)

    start_time = (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"

    all_items = []
    request = service.activities().list(
        userKey='all',
        applicationName='meet',
        maxResults=10,
        # startTime=start_time
    )
    
    while request is not None:
        response = request.execute()
        items = response.get('items', [])

        # If meeting_code is provided, filter results
        if meeting_code:
            items = [
                item for item in items
                if any(
                    param.get('name') == 'meeting_code' and param.get('value') == meeting_code
                    for param in item.get('events', [])[0].get('parameters', [])
                )
            ]

        all_items.extend(items)
        request = service.activities().list_next(request, response)

    return all_items
