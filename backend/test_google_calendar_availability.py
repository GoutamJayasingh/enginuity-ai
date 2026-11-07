from pprint import pprint

from app.services.google_calendar_service import (
    check_calendar_availability,
)


result = check_calendar_availability(
    time_min="2026-11-10T09:00:00+05:30",
    time_max="2026-11-10T18:00:00+05:30",
)

pprint(result)