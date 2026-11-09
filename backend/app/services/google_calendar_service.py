import os
from pathlib import Path

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]



def get_google_calendar_service():

    credentials_path = os.getenv(
        "GOOGLE_CLIENT_SECRET_FILE"
    )

    token_path = os.getenv(
        "GOOGLE_TOKEN_FILE"
    )

    if not credentials_path or not token_path:
        raise ValueError(
            "Google Calendar OAuth file paths are not configured."
        )

    credentials_file = BASE_DIR / credentials_path
    token_file = BASE_DIR / token_path

    if not credentials_file.exists():
        raise FileNotFoundError(
            f"Google OAuth credentials file not found: {credentials_file}"
        )

    credentials = None

    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_file),
            SCOPES,
        )

    if credentials and credentials.expired and credentials.refresh_token:

        credentials.refresh(Request())

        token_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        token_file.write_text(
            credentials.to_json()
        )

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
    if not isinstance(max_results, int) or isinstance(max_results, bool):
        raise ValueError("max_results must be an integer.")

    if not 1 <= max_results <= 2500:
        raise ValueError("max_results must be between 1 and 2500.")
    
    service = get_google_calendar_service()

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    try:
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

    except HttpError as error:
        return handle_google_calendar_error(error)

    events = events_result.get("items", [])

    
    return {
        "success": True,
        "data": {
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
        },
        "message": "Calendar events retrieved successfully.",
    }


def check_calendar_availability(
    time_min: str,
    time_max: str,
):

    validate_time_range(
        time_min,
        time_max,
    )


    service = get_google_calendar_service()

    
    try:
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

    except HttpError as error:
        return handle_google_calendar_error(error)


    calendar_data = response.get(
        "calendars", {}
    ).get("primary", {})

    busy_periods = calendar_data.get(
        "busy", []
    )

    
    return {
        "success": True,
        "data": {
            "calendar_id": "primary",
            "time_min": time_min,
            "time_max": time_max,
            "is_available": len(busy_periods) == 0,
            "busy_periods": busy_periods,
        },
        "message": "Calendar availability checked successfully.",
    }


def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = None,
    location: str = None,
):
    if not summary.strip():
        raise ValueError("Event summary cannot be empty.")

    validate_time_range(
        start_time,
        end_time,
    )

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

    try:
        created_event = service.events().insert(
            calendarId="primary",
            body=event,
        ).execute()

    except HttpError as error:
        return handle_google_calendar_error(error)

    
    return {
        "success": True,
        "data": {
            "event_id": created_event.get("id"),
            "summary": created_event.get("summary"),
            "start": created_event.get("start"),
            "end": created_event.get("end"),
            "status": created_event.get("status"),
            "html_link": created_event.get("htmlLink"),
        },
        "message": "Calendar event created successfully.",
    }


def delete_calendar_event(
    event_id: str,
):
    service = get_google_calendar_service()

    try:
        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

    except HttpError as error:
        return handle_google_calendar_error(error)
    
    
    return {
        "success": True,
        "data": {
            "event_id": event_id,
            "deleted": True,
        },
        "message": "Calendar event deleted successfully.",
    }


def update_calendar_event(
    event_id: str,
    summary: str = None,
    start_time: str = None,
    end_time: str = None,
    description: str = None,
    location: str = None,
):
    service = get_google_calendar_service()

    event_updates = {}

    if summary is not None:
        event_updates["summary"] = summary

    if start_time is not None:
        event_updates["start"] = {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata",
        }

    if end_time is not None:
        event_updates["end"] = {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata",
        }

    if description is not None:
        event_updates["description"] = description

    if location is not None:
        event_updates["location"] = location

    if not event_updates:
        raise ValueError("At least one field must be provided for update.")


    if "summary" in event_updates and not event_updates["summary"].strip():
        raise ValueError("Event summary cannot be empty.")

    if start_time is not None or end_time is not None:

        current_event = service.events().get(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        effective_start = (
            start_time
            if start_time is not None
            else current_event["start"].get("dateTime")
        )

        effective_end = (
            end_time
            if end_time is not None
            else current_event["end"].get("dateTime")
        )

        if effective_start is None or effective_end is None:
            raise ValueError(
                "Updating date-only events is not supported by this operation."
            )

        validate_time_range(
            effective_start,
            effective_end,
        )

    try:
        updated_event = service.events().patch(
            calendarId="primary",
            eventId=event_id,
            body=event_updates,
        ).execute()

    except HttpError as error:
        return handle_google_calendar_error(error)

    
    return {
        "success": True,
        "data": {
            "event_id": updated_event.get("id"),
            "summary": updated_event.get("summary"),
            "start": updated_event.get("start"),
            "end": updated_event.get("end"),
            "description": updated_event.get("description"),
            "location": updated_event.get("location"),
            "status": updated_event.get("status"),
            "html_link": updated_event.get("htmlLink"),
        },
        "message": "Calendar event updated successfully.",
    }



def validate_time_range(
    start_time: str,
    end_time: str,
):
    try:
        start = datetime.fromisoformat(
            start_time.replace("Z", "+00:00")
        )

        end = datetime.fromisoformat(
            end_time.replace("Z", "+00:00")
        )

    except ValueError:
        raise ValueError(
            "Invalid date-time format. Use ISO 8601 format."
        )

    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError(
            "Start and end times must include timezone information."
        )

    if start >= end:
        raise ValueError(
            "Start time must be earlier than end time."
        )


def handle_google_calendar_error(error: HttpError):
    status_code = (
        error.resp.status
        if error.resp
        else None
    )

    if status_code == 401:
        message = "Google Calendar authentication failed."

    elif status_code == 403:
        message = "Permission denied by Google Calendar."

    elif status_code == 404:
        message = "Google Calendar resource not found."

    elif status_code == 410:
        message = "Google Calendar resource has been deleted."

    elif status_code == 429:
        message = "Google Calendar API rate limit exceeded."

    elif status_code and status_code >= 500:
        message = "Google Calendar service is temporarily unavailable."

    else:
        message = "Google Calendar API request failed."

    return {
        "success": False,
        "status_code": status_code,
        "message": message,
        "details": str(error),
    }


