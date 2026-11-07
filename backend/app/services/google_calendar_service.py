import os
from pathlib import Path

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_google_calendar_service():

    credentials_file = (
        BASE_DIR / os.getenv(
            "GOOGLE_CLIENT_SECRET_FILE"
        )
    )

    token_file = (
        BASE_DIR / os.getenv(
            "GOOGLE_TOKEN_FILE"
        )
    )

    credentials = None

    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_file),
            SCOPES,
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file),
            SCOPES,
        )

        credentials = flow.run_local_server(
            port=0
        )

        token_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        token_file.write_text(
            credentials.to_json()
        )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )

def get_upcoming_events(
    max_results: int = 10,
):
    service = get_google_calendar_service()

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    return {
        "total": len(events),
        "events": [
            {
                "id": event.get("id"),
                "summary": event.get("summary"),
                "description": event.get("description"),
                "location": event.get("location"),
                "start": event.get("start"),
                "end": event.get("end"),
                "status": event.get("status"),
                "html_link": event.get("htmlLink"),
            }
            for event in events
        ],
    }

def check_calendar_availability(
    time_min: str,
    time_max: str,
):
    service = get_google_calendar_service()

    response = service.freebusy().query(
        body={
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "Asia/Kolkata",
            "items": [
                {
                    "id": "primary"
                }
            ],
        }
    ).execute()

    calendar_data = response.get(
        "calendars", {}
    ).get("primary", {})

    busy_periods = calendar_data.get(
        "busy", []
    )

    return {
        "calendar_id": "primary",
        "time_min": time_min,
        "time_max": time_max,
        "is_available": len(busy_periods) == 0,
        "busy_periods": busy_periods,
    }

def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = None,
    location: str = None,
):
    service = get_google_calendar_service()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata",
        },
    }

    if description:
        event["description"] = description

    if location:
        event["location"] = location

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
    ).execute()

    return {
        "id": created_event.get("id"),
        "summary": created_event.get("summary"),
        "start": created_event.get("start"),
        "end": created_event.get("end"),
        "status": created_event.get("status"),
        "html_link": created_event.get("htmlLink"),
    }