
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.github_repository import GitHubRepository
from app.models.commit import Commit
from app.models.pull_request import PullRequest
from app.models.project import Project


def get_project_github_context(
    project_id: int,
    db: Session
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    repositories = (
        db.query(GitHubRepository)
        .filter(
            GitHubRepository.project_id == project_id
        )
        .all()
    )

    repository_context = []

    for repository in repositories:
        commits = (
            db.query(Commit)
            .filter(
                Commit.repository_id == repository.id
            )
            .order_by(Commit.committed_at.desc())
            .all()
        )

        pull_requests = (
            db.query(PullRequest)
            .filter(
                PullRequest.repository_id == repository.id
            )
            .order_by(PullRequest.updated_at.desc())
            .all()
        )

        repository_context.append({
            "repository": {
                "id": repository.id,
                "name": repository.repo_name,
                "full_name": repository.full_name,
                "url": repository.repo_url,
                "default_branch": repository.default_branch,
                "language": repository.language,
            },
            "commits": [
                {
                    "sha": commit.sha,
                    "message": commit.message,
                    "author_name": commit.author_name,
                    "committed_at": commit.committed_at,
                }
                for commit in commits
            ],
            "pull_requests": [
                {
                    "github_id": pull_request.github_id,
                    "number": pull_request.number,
                    "title": pull_request.title,
                    "state": pull_request.state,
                    "author_name": pull_request.author_name,
                    "merged": pull_request.merged,
                    "updated_at": pull_request.updated_at,
                }
                for pull_request in pull_requests
            ],
        })

    return {
        "project_id": project.id,
        "repositories": repository_context,
        "repository_count": len(repository_context),
        "commit_count": sum(
            len(item["commits"])
            for item in repository_context
        ),
        "pull_request_count": sum(
            len(item["pull_requests"])
            for item in repository_context
        ),
    }
