from mcp.server.mcpserver import MCPServer

from app.db.session import SessionLocal
from app.models.project import Project

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


if __name__ == "__main__":
    server.run(transport="stdio")

