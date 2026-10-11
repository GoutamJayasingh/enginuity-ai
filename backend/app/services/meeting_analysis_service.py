import os

from app.core.llm_config import get_groq_client
from app.schemas.meeting_analysis import MeetingAnalysisResult
from app.services.meeting_analysis_prompt import (
    build_meeting_analysis_prompt,
)

from sqlalchemy.orm import Session

from app.services.meeting_decision_service import (
    create_meeting_decision,
)

from app.services.meeting_action_item_service import (
    create_meeting_action_item,
)

from app.services.meeting_blocker_service import (
    create_meeting_blocker,
)

from app.services.meeting_risk_service import (
    create_meeting_risk,
)

from fastapi import HTTPException, status
from groq import APIConnectionError, APIStatusError, RateLimitError
from pydantic import ValidationError

def analyze_meeting_content(
    meeting_content: str,
) -> MeetingAnalysisResult:
    if not meeting_content or not meeting_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting content cannot be empty.",
        )

    try:
        client = get_groq_client()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM configuration is unavailable.",
        ) from exc

    prompt = build_meeting_analysis_prompt(meeting_content)

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
                        "You analyze engineering meeting notes and "
                        "return structured information as valid JSON."
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

    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="The LLM rate limit was reached. Try again later.",
        ) from exc

    except APIConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to the LLM provider.",
        ) from exc

    except APIStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The LLM provider rejected or could not process "
                "the analysis request. Check the model configuration "
                "and provider availability."
            ),
        ) from exc

    response_content = response.choices[0].message.content

    if not response_content:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The LLM returned an empty response.",
        )

    try:
        result = MeetingAnalysisResult.model_validate_json(
            response_content
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The LLM returned an invalid analysis structure.",
        ) from exc

    return validate_meeting_analysis(result)

def validate_meeting_analysis(
    result: MeetingAnalysisResult,
) -> MeetingAnalysisResult:
    def clean_unique_items(items, field_name: str):
        seen = set()
        cleaned_items = []

        for item in items:
            description = getattr(item, field_name).strip()

            if not description:
                raise ValueError(
                    f"{field_name} cannot be empty or whitespace."
                )

            normalized = " ".join(description.split()).casefold()

            if normalized in seen:
                continue

            seen.add(normalized)
            setattr(item, field_name, description)

            cleaned_items.append(item)

        return cleaned_items

    result.decisions = clean_unique_items(
        result.decisions, "decision"
    )
    result.action_items = clean_unique_items(
        result.action_items, "action_item"
    )
    result.blockers = clean_unique_items(
        result.blockers, "blocker"
    )
    result.risks = clean_unique_items(
        result.risks, "risk"
    )

    for action in result.action_items:
        if action.assignee is not None:
            action.assignee = action.assignee.strip() or None

    return result

def persist_meeting_decisions(
    result: MeetingAnalysisResult,
    meeting_note_id: int,
    db: Session,
):
    saved_decisions = []

    for item in result.decisions:
        saved_decision = create_meeting_decision(
            decision=item.decision,
            meeting_note_id=meeting_note_id,
            db=db,
            commit=False,
        )

        saved_decisions.append(saved_decision)

    return saved_decisions

def persist_meeting_action_items(
    result: MeetingAnalysisResult,
    meeting_note_id: int,
    db: Session,
):
    saved_action_items = []

    for item in result.action_items:
        saved_action_item = create_meeting_action_item(
            action_item=item.action_item,
            assignee=item.assignee,
            due_date=item.due_date,
            meeting_note_id=meeting_note_id,
            db=db,
            commit=False,
        )

        saved_action_items.append(saved_action_item)

    return saved_action_items

def persist_meeting_blockers(
    result: MeetingAnalysisResult,
    meeting_note_id: int,
    db: Session,
):
    saved_blockers = []

    for item in result.blockers:
        saved_blocker = create_meeting_blocker(
            blocker=item.blocker,
            severity=item.severity,
            meeting_note_id=meeting_note_id,
            db=db,
            commit=False,
        )

        saved_blockers.append(saved_blocker)

    return saved_blockers

def persist_meeting_risks(
    result: MeetingAnalysisResult,
    meeting_note_id: int,
    db: Session,
):
    saved_risks = []

    for item in result.risks:
        saved_risk = create_meeting_risk(
            risk=item.risk,
            severity=item.severity,
            meeting_note_id=meeting_note_id,
            db=db,
            commit=False,
        )

        saved_risks.append(saved_risk)

    return saved_risks

