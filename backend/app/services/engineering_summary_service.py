
from app.services.project_context_service import (
    get_project_github_context,
)


def build_engineering_summary(
    project_id: int,
    db,
):
    context = get_project_github_context(
        project_id=project_id,
        db=db,
    )

    total_decisions = sum(
        len(meeting["decisions"])
        for meeting in context["meetings"]
    )

    total_action_items = sum(
        len(meeting["action_items"])
        for meeting in context["meetings"]
    )

    total_blockers = sum(
        len(meeting["blockers"])
        for meeting in context["meetings"]
    )

    total_risks = sum(
        len(meeting["risks"])
        for meeting in context["meetings"]
    )

    pending_action_items = sum(
        1
        for meeting in context["meetings"]
        for item in meeting["action_items"]
        if (item["status"] or "").strip().casefold()
        == "pending"
    )

    open_blockers = sum(
        1
        for meeting in context["meetings"]
        for blocker in meeting["blockers"]
        if (blocker["status"] or "").strip().casefold()
        == "open"
    )

    open_risks = sum(
        1
        for meeting in context["meetings"]
        for risk in meeting["risks"]
        if (risk["status"] or "").strip().casefold()
        == "open"
    )

    return {
        "project_id": context["project_id"],
        "github": {
            "repository_count": context["repository_count"],
            "commit_count": context["commit_count"],
            "pull_request_count": context["pull_request_count"],
        },
        "meetings": {
            "meeting_count": context["meeting_count"],
            "decision_count": total_decisions,
            "action_item_count": total_action_items,
            "pending_action_item_count": pending_action_items,
            "blocker_count": total_blockers,
            "open_blocker_count": open_blockers,
            "risk_count": total_risks,
            "open_risk_count": open_risks,
        },
        "summary": {
            "pending_action_items": pending_action_items,
            "open_blockers": open_blockers,
            "open_risks": open_risks,
        },
    }
