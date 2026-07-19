from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.github_service import (
    sync_repositories,
    link_repository_to_project,
    fetch_repository_commits
)
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/github",
    tags=["GitHub"]
)


@router.post("/sync")
def sync_github_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    synced = sync_repositories(db)

    return {
        "message": "GitHub repositories synchronized successfully.",
        "repositories_added": len(synced),
        "repositories": synced
    }

@router.post(
    "/projects/{project_id}/link-repository/{repository_id}"
)
def link_repository(
    project_id: int,
    repository_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repository = link_repository_to_project(
        project_id=project_id,
        repository_id=repository_id,
        db=db
    )

    return {
        "message": "Repository linked successfully.",
        "repository": {
            "id": repository.id,
            "name": repository.repo_name,
            "project_id": repository.project_id
        }
    }

@router.get(
    "/repositories/{repository_id}/commits"
)
def get_commits(
    repository_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    commits = fetch_repository_commits(
        repository_id=repository_id,
        db=db
    )

    return {
        "message": "Commits synchronized successfully.",
        "repository_id": repository_id,
        "commits_added": len(commits),
        "commit_shas": commits
    }