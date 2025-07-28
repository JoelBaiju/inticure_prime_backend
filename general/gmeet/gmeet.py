from __future__ import print_function
import datetime
import os.path
import uuid
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).resolve().parent.parent

def generate_google_meet(summary, description, start_time, end_time, timezone='Asia/Kolkata'):
    """
    Generate a Google Meet link by creating a calendar event
    
    Args:
        summary: Event title (string)
        description: Event description (string)
        start_time: Start time (datetime object or ISO format string)
        end_time: End time (datetime object or ISO format string)
        timezone: Timezone string (default: 'Asia/Kolkata')
    
    Returns:
        Google Meet URL (string) or None if failed
    """
    print("Starting generate_google_meet function")
    
    # First handle credentials
    try:
        creds = None
        token_path = os.path.join(BASE_DIR, 'gmeet/token.json')
        client_secret_path = os.path.join(BASE_DIR, 'gmeet/client_secret.json')

        # Load credentials if token exists
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If no valid credentials, go through the OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save credentials for future use
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
    except Exception as e:
        print("Error during credentials setup:", e)
        return None

    # Process time inputs
    try:
        # Convert datetime objects to ISO strings
        if isinstance(start_time, datetime.datetime):
            start_time = start_time.isoformat()
        if isinstance(end_time, datetime.datetime):
            end_time = end_time.isoformat()

        # Ensure strings are in proper format
        if isinstance(start_time, str):
            if 'T' not in start_time:  # If just date provided
                start_time = f"{start_time}T00:00:00"
            if start_time.count(':') == 1:  # If missing seconds
                start_time = start_time + ':00'
                
        if isinstance(end_time, str):
            if 'T' not in end_time:
                end_time = f"{end_time}T00:00:00"
            if end_time.count(':') == 1:
                end_time = end_time + ':00'

        # Create the calendar service
        service = build('calendar', 'v3', credentials=creds)

        event = {
            "conferenceDataVersion": 1,
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
            'conferenceData': {
                'createRequest': {
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    },
                    'requestId': str(uuid.uuid4()),
                }
            },
            'visibility': 'public',
            'anyoneCanAddSelf': True,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event_result = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        print('Event created:', event_result.get('htmlLink'))
        return event_result.get('hangoutLink')

    except HttpError as error:
        print('Google API error occurred:', error)
        return None
    except Exception as error:
        print('An unexpected error occurred:', error)
        return None