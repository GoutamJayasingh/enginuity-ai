from pprint import pprint

from app.services.google_calendar_service import (
    get_upcoming_events,
)


result = get_upcoming_events(
    max_results=10,
)

pprint(result)