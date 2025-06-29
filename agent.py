import os
import re
from datetime import datetime, timedelta

import dateparser
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Google Calendar Auth
def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '968893385878-18lck22286ptqecc50fui4062sfm9hkh.apps.googleusercontent.json',
            SCOPES
        )
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def extract_datetime(message: str):
    dt = dateparser.parse(
        message,
        settings={
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False
        }
    )
    return dt

def check_calendar_availability(service, date):
    events_result = service.events().list(
        calendarId='primary',
        timeMin=f"{date}T00:00:00Z",
        timeMax=f"{date}T23:59:59Z",
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    busy_slots = []
    for event in events:
        busy_slots.append({
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "end": event["end"].get("dateTime", event["end"].get("date")),
            "summary": event.get("summary", "")
        })
    return busy_slots


# New conversation state
conversation_state = {
    "awaiting_time": False
}


def process_message(msg: str) -> str:
    global conversation_state
    try:
        msg_lower = msg.lower()

        # If we are waiting for time, parse it
        if conversation_state["awaiting_time"]:
            dt = extract_datetime(msg)
            if dt is None:
                return (
                    "I couldn't understand the time. "
                    "Please try e.g. 'Tomorrow at 3 PM' or 'in 2 hours'."
                )
            
            # Book the event
            service = get_calendar_service()
            
            start_dt_utc = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_dt_obj = dt + timedelta(hours=1)
            end_dt_utc = end_dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

            event = {
                'summary': 'Meeting booked by Lyra AI',
                'start': {
                    'dateTime': start_dt_utc,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_dt_utc,
                    'timeZone': 'UTC',
                },
            }

            service.events().insert(calendarId='primary', body=event).execute()

            conversation_state["awaiting_time"] = False
            return f"Your meeting is booked for {dt.strftime('%A, %d %B %Y at %I:%M %p')}."

        # Otherwise, check if user wants to book
        if "book" in msg_lower or "schedule" in msg_lower:
            conversation_state["awaiting_time"] = True
            return (
                "I'd love to help you book! "
                "Please tell me the time, e.g.: "
                "'Tomorrow at 3 PM', 'Next Monday 10 AM', or 'In 2 hours'."
            )

        return "I'm Lyra, your AI scheduling assistant. Tell me when you'd like to book a meeting!"

    except Exception as e:
        return f"Error: {str(e)}"
