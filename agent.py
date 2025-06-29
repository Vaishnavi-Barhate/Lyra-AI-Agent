import os
from datetime import datetime, timedelta

import dateparser
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


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


def process_message(msg: str, conversation_state: dict) -> dict:
    """
    Processes user message and returns:
        - reply: str
        - updated conversation_state: dict
    """

    try:
        msg_lower = msg.lower()

        # Check if waiting for time
        if conversation_state.get("awaiting_time", False):
            dt = extract_datetime(msg)
            if dt is None:
                return {
                    "reply": (
                        "⚠️ I couldn't understand the time. "
                        "Please try something like 'Tomorrow at 3 PM' or 'in 2 hours'."
                    ),
                    "conversation_state": conversation_state
                }

            # Book the meeting
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
            return {
                "reply": f"✅ Your meeting is booked for {dt.strftime('%A, %d %B %Y at %I:%M %p')}!",
                "conversation_state": conversation_state
            }

        # Check if user wants to book
        if "book" in msg_lower or "schedule" in msg_lower:
            conversation_state["awaiting_time"] = True
            return {
                "reply": (
                    "✅ I'd love to help you book! "
                    "Please tell me a time, e.g.: "
                    "'Tomorrow at 3 PM', 'Next Monday 10 AM', or 'In 2 hours'."
                ),
                "conversation_state": conversation_state
            }

        return {
            "reply": "Hi! I'm Lyra, your AI scheduling assistant. Tell me when you'd like to book a meeting.",
            "conversation_state": conversation_state
        }

    except Exception as e:
        return {
            "reply": f"❌ Error: {str(e)}",
            "conversation_state": conversation_state
        }
