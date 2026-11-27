
from unittest.mock import MagicMock, patch

from app.services.google_calendar_service import (
    get_upcoming_events,
)


def main():

    first_page = {
        "items": [
            {"id": "event_1", "summary": "Event 1"},
            {"id": "event_2", "summary": "Event 2"},
        ],
        "nextPageToken": "next_page_token",
    }

    second_page = {
        "items": [
            {"id": "event_3", "summary": "Event 3"},
            {"id": "event_4", "summary": "Event 4"},
        ],
    }

    mock_service = MagicMock()

    mock_events_resource = MagicMock()
    mock_list = MagicMock()

    mock_service.events.return_value = mock_events_resource
    mock_events_resource.list = mock_list

    mock_list.return_value.execute.side_effect = [
        first_page,
        second_page,
    ]

    with patch(
        "app.services.google_calendar_service.get_google_calendar_service",
        return_value=mock_service,
    ):

        result = get_upcoming_events(max_results=4)

    assert result["success"] is True
    assert result["data"]["total"] == 4

    assert [
        event["id"]
        for event in result["data"]["events"]
    ] == [
        "event_1",
        "event_2",
        "event_3",
        "event_4",
    ]

    assert mock_list.call_count == 2

    print("Pagination test passed!")
    print("Pages retrieved: 2")
    print("Total events retrieved:", result["data"]["total"])


if __name__ == "__main__":
    main()
