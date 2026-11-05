from mcp.server.mcpserver import MCPServer

from app.db.session import SessionLocal
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.meeting_note import MeetingNote
from app.models.meeting_decision import MeetingDecision
from app.models.meeting_action_item import MeetingActionItem
from app.models.meeting_blocker import MeetingBlocker
from app.models.meeting_risk import MeetingRisk
from app.models.github_repository import GitHubRepository

import app.db.base_imports

server = MCPServer(
    name="enginuity-ai",
    version="1.0.0",
)


@server.tool()
def get_server_status() -> str:
    """Return the current status of the Enginuity-AI MCP server."""

    return "Enginuity-AI MCP Server is running."

@server.tool()
def get_project_details(
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve project details for a specific project owner."""

    db = SessionLocal()

    try:
        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not project:
            return {
                "success": False,
                "message": "Project not found.",
            }

        return {
            "success": True,
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_at": (
                    project.created_at.isoformat()
                    if project.created_at
                    else None
                ),
                "owner_id": project.owner_id,
                "github_sync_enabled": project.github_sync_enabled,
            },
        }

    finally:
        db.close()

@server.tool()
def get_all_projects(
    owner_id: int,
) -> dict:
    """Retrieve all projects belonging to a specific owner."""

    db = SessionLocal()

    try:
        projects = (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .all()
        )

        return {
            "success": True,
            "total_projects": len(projects),
            "projects": [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "created_at": (
                        project.created_at.isoformat()
                        if project.created_at
                        else None
                    ),
                    "github_sync_enabled": project.github_sync_enabled,
                }
                for project in projects
            ],
        }

    finally:
        db.close()

@server.tool()
def get_project_sprints(
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve all sprints belonging to a specific project."""

    db = SessionLocal()

    try:
        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not project:
            return {
                "success": False,
                "message": "Project not found.",
            }

        sprints = (
            db.query(Sprint)
            .filter(Sprint.project_id == project_id)
            .order_by(Sprint.start_date.desc())
            .all()
        )

        return {
            "success": True,
            "project_id": project_id,
            "total_sprints": len(sprints),
            "sprints": [
                {
                    "id": sprint.id,
                    "name": sprint.name,
                    "goal": sprint.goal,
                    "start_date": (
                        sprint.start_date.isoformat()
                        if sprint.start_date
                        else None
                    ),
                    "end_date": (
                        sprint.end_date.isoformat()
                        if sprint.end_date
                        else None
                    ),
                    "status": sprint.status,
                    "created_at": (
                        sprint.created_at.isoformat()
                        if sprint.created_at
                        else None
                    ),
                }
                for sprint in sprints
            ],
        }

    finally:
        db.close()

@server.tool()
def get_project_meetings(
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve all meeting notes belonging to a project."""

    db = SessionLocal()

    try:
        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not project:
            return {
                "success": False,
                "message": "Project not found.",
            }

        meetings = (
            db.query(MeetingNote)
            .filter(MeetingNote.project_id == project_id)
            .order_by(MeetingNote.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "project_id": project_id,
            "total_meetings": len(meetings),
            "meetings": [
                {
                    "id": meeting.id,
                    "title": meeting.title,
                    "content": meeting.content,
                    "summary": meeting.summary,
                    "created_at": (
                        meeting.created_at.isoformat()
                        if meeting.created_at
                        else None
                    ),
                }
                for meeting in meetings
            ],
        }

    finally:
        db.close()

@server.tool()
def get_meeting_decisions(
    meeting_id: int,
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve all decisions associated with a project meeting."""

    db = SessionLocal()

    try:
        meeting = (
            db.query(MeetingNote)
            .join(Project)
            .filter(
                MeetingNote.id == meeting_id,
                MeetingNote.project_id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not meeting:
            return {
                "success": False,
                "message": "Meeting not found.",
            }

        decisions = (
            db.query(MeetingDecision)
            .filter(
                MeetingDecision.meeting_note_id == meeting_id
            )
            .order_by(MeetingDecision.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "meeting_id": meeting_id,
            "total_decisions": len(decisions),
            "decisions": [
                {
                    "id": decision.id,
                    "decision": decision.decision,
                    "created_at": (
                        decision.created_at.isoformat()
                        if decision.created_at
                        else None
                    ),
                }
                for decision in decisions
            ],
        }

    finally:
        db.close()

@server.tool()
def get_meeting_action_items(
    meeting_id: int,
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve all action items associated with a project meeting."""

    db = SessionLocal()

    try:
        meeting = (
            db.query(MeetingNote)
            .join(Project)
            .filter(
                MeetingNote.id == meeting_id,
                MeetingNote.project_id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not meeting:
            return {
                "success": False,
                "message": "Meeting not found.",
            }

        action_items = (
            db.query(MeetingActionItem)
            .filter(
                MeetingActionItem.meeting_note_id == meeting_id
            )
            .order_by(MeetingActionItem.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "meeting_id": meeting_id,
            "total_action_items": len(action_items),
            "action_items": [
                {
                    "id": item.id,
                    "action_item": item.action_item,
                    "assignee": item.assignee,
                    "due_date": (
                        item.due_date.isoformat()
                        if item.due_date
                        else None
                    ),
                    "status": item.status,
                    "created_at": (
                        item.created_at.isoformat()
                        if item.created_at
                        else None
                    ),
                }
                for item in action_items
            ],
        }

    finally:
        db.close()

@server.tool()
def get_meeting_blockers(
    meeting_id: int,
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve all blockers associated with a project meeting."""

    db = SessionLocal()

    try:
        meeting = (
            db.query(MeetingNote)
            .join(Project)
            .filter(
                MeetingNote.id == meeting_id,
                MeetingNote.project_id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not meeting:
            return {
                "success": False,
                "message": "Meeting not found.",
            }

        blockers = (
            db.query(MeetingBlocker)
            .filter(
                MeetingBlocker.meeting_note_id == meeting_id
            )
            .order_by(MeetingBlocker.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "meeting_id": meeting_id,
            "total_blockers": len(blockers),
            "blockers": [
                {
                    "id": blocker.id,
                    "blocker": blocker.blocker,
                    "severity": blocker.severity,
                    "status": blocker.status,
                    "created_at": (
                        blocker.created_at.isoformat()
                        if blocker.created_at
                        else None
                    ),
                }
                for blocker in blockers
            ],
        }

    finally:
        db.close()

@server.tool()
def get_meeting_risks(
    meeting_id: int,
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve all risks associated with a project meeting."""

    db = SessionLocal()

    try:
        meeting = (
            db.query(MeetingNote)
            .join(Project)
            .filter(
                MeetingNote.id == meeting_id,
                MeetingNote.project_id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not meeting:
            return {
                "success": False,
                "message": "Meeting not found.",
            }

        risks = (
            db.query(MeetingRisk)
            .filter(
                MeetingRisk.meeting_note_id == meeting_id
            )
            .order_by(MeetingRisk.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "meeting_id": meeting_id,
            "total_risks": len(risks),
            "risks": [
                {
                    "id": risk.id,
                    "risk": risk.risk,
                    "severity": risk.severity,
                    "status": risk.status,
                    "created_at": (
                        risk.created_at.isoformat()
                        if risk.created_at
                        else None
                    ),
                }
                for risk in risks
            ],
        }

    finally:
        db.close()

@server.tool()
def get_project_github_repositories(
    project_id: int,
    owner_id: int,
) -> dict:
    """Retrieve GitHub repositories linked to a project."""

    db = SessionLocal()

    try:
        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not project:
            return {
                "success": False,
                "message": "Project not found.",
            }

        repositories = (
            db.query(GitHubRepository)
            .filter(
                GitHubRepository.project_id == project_id
            )
            .all()
        )

        return {
            "success": True,
            "project_id": project_id,
            "total_repositories": len(repositories),
            "repositories": [
                {
                    "id": repo.id,
                    "repo_name": repo.repo_name,
                    "full_name": repo.full_name,
                    "repo_url": repo.repo_url,
                    "description": repo.description,
                    "owner_name": repo.owner_name,
                    "private": repo.private,
                    "default_branch": repo.default_branch,
                    "language": repo.language,
                    "stars": repo.stars,
                    "forks": repo.forks,
                    "connected_at": (
                        repo.connected_at.isoformat()
                        if repo.connected_at
                        else None
                    ),
                }
                for repo in repositories
            ],
        }

    finally:
        db.close()


if __name__ == "__main__":
    server.run(transport="stdio")

