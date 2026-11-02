import os
import json

from groq import RateLimitError, APIConnectionError, APIStatusError
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.core.llm_config import get_groq_client
from app.schemas.engineering_insights import EngineeringInsightsResult
from app.services.project_context_service import get_project_github_context
from app.services.engineering_summary_service import build_engineering_summary
from app.services.engineering_insights_prompt import (
    build_engineering_insights_prompt,
)

from datetime import datetime
from sqlalchemy.orm import Session

from app.models.engineering_insight import EngineeringInsight


def generate_engineering_insights(
    project_id: int,
    db,
) -> EngineeringInsightsResult:

    # Step 1: Retrieve unified project context
    project_context = get_project_github_context(
        project_id=project_id,
        db=db,
    )

    # Step 2: Build engineering summary
    engineering_summary = build_engineering_summary(
        project_id=project_id,
        db=db,
    )

    # Step 3: Build AI prompt
    prompt = build_engineering_insights_prompt(
        project_context=project_context,
        engineering_summary=engineering_summary,
    )

    # Step 4: Initialize Groq client
    client = get_groq_client()

    # Step 5: Generate AI insights
    try:
        response = client.chat.completions.create(
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-20b",
            ),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an engineering intelligence "
                        "assistant. Follow the provided instructions "
                        "and return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI provider rate limit exceeded.",
        )

    except APIConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to the AI provider.",
        )

    except APIStatusError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned an error.",
        )

    # Step 6: Extract and validate AI response
    try:
        response_content = response.choices[0].message.content

        if not response_content:
            raise ValueError("AI provider returned an empty response.")

        insights_data = json.loads(response_content)

        validated_insights = EngineeringInsightsResult.model_validate(
            insights_data
        )

        return validated_insights

    except (json.JSONDecodeError, ValidationError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned an invalid engineering insights response.",
        )

def persist_engineering_insights(
    project_id: int,
    insights: EngineeringInsightsResult,
    db: Session,
) -> EngineeringInsight:

    engineering_insight = EngineeringInsight(
        project_id=project_id,
        insights=insights.model_dump(),
        model_name=os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        ),
        prompt_version="v1",
        generated_at=datetime.utcnow(),
    )

    db.add(engineering_insight)

    try:
        db.commit()
        db.refresh(engineering_insight)

    except Exception:
        db.rollback()
        raise

    return engineering_insight