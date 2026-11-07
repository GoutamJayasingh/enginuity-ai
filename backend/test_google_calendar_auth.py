from app.services.google_calendar_service import (
    get_google_calendar_service,
)


service = get_google_calendar_service()

print("Google Calendar authentication successful!")

calendar = service.calendarList().get(
    calendarId="primary"
).execute()

print("Connected calendar:", calendar["summary"])