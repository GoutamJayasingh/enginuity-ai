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