import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. "
            "Add it to the backend .env file."
        )

    return Groq(api_key=api_key)