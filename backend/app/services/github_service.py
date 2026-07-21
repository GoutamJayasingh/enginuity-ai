import os

from dotenv import load_dotenv
from github import Github

from fastapi import HTTPException, status

from app.models.user import User

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment variables")

github = Github(GITHUB_TOKEN)


def get_authenticated_user():
    """
    Fetch the authenticated GitHub user's profile.
    """

    user = github.get_user()

    return {
        "username": user.login,
        "name": user.name,
        "bio": user.bio,
        "public_repos": user.public_repos,
        "followers": user.followers,
        "following": user.following,
        "profile_url": user.html_url,
        "avatar_url": user.avatar_url,
    }

def get_user_repositories():
    """
    Fetch all repositories of the authenticated user.
    """

    repositories = github.get_user().get_repos()

    repo_list = []

    for repo in repositories:
        repo_list.append({
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": repo.private,
            "default_branch": repo.default_branch,
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "html_url": repo.html_url,
        })

    return repo_list

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.github_repository import GitHubRepository


def sync_repositories(db: Session):
    """
    Synchronize GitHub repositories into PostgreSQL.
    """

    repositories = get_user_repositories()

    synced = []

    for repo in repositories:

        existing_repo = (
            db.query(GitHubRepository)
            .filter(
                GitHubRepository.full_name == repo["full_name"]
            )
            .first()
        )

        if existing_repo:
            continue

        github_repo = GitHubRepository(
            repo_name=repo["name"],
            full_name=repo["full_name"],
            repo_url=repo["html_url"],
            description=repo["description"],
            owner_name=repo["full_name"].split("/")[0],
            private=repo["private"],
            default_branch=repo["default_branch"],
            language=repo["language"],
            stars=repo["stars"],
            forks=repo["forks"],
        )

        db.add(github_repo)

        synced.append(repo["full_name"])

    db.commit()

    return synced

def link_repository_to_project(
    project_id: int,
    repository_id: int,
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

    repository = (
        db.query(GitHubRepository)
        .filter(GitHubRepository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found."
        )
    
    if (
        repository.project_id is not None
        and repository.project_id != project.id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Repository is already linked to another project."
        )

    repository.project_id = project.id

    db.commit()

    db.refresh(repository)

    return repository

def get_repository_commits(
    owner: str,
    repository_name: str
):
    """
    Fetch commit history for a GitHub repository.
    """

    repository = github.get_repo(
        f"{owner}/{repository_name}"
    )

    commits = repository.get_commits()

    return commits

from app.models.commit import Commit

def fetch_repository_commits(
    repository_id: int,
    db: Session
):
    """
    Fetch commit history for a linked repository.
    """

    repository = (
        db.query(GitHubRepository)
        .filter(
            GitHubRepository.id == repository_id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found."
        )

    commits = list(
        get_repository_commits(
            owner=repository.owner_name,
            repository_name=repository.repo_name
        )
    )

    synced = []

    new_commits = 0
    duplicate_commits = 0

    for commit in commits:
        existing_commit = (
            db.query(Commit)
            .filter(
                Commit.sha == commit.sha
            )
            .first()
        )

        if existing_commit:
            duplicate_commits += 1
            continue

        new_commit = Commit(
            sha=commit.sha,
            message=commit.commit.message,
            author_name=commit.commit.author.name,
            author_email=commit.commit.author.email,
            committed_at=commit.commit.author.date,
            repository_id=repository.id
        )

        db.add(new_commit)

        synced.append(commit.sha)

        new_commits += 1

    db.commit()

    return {
        "repository": repository.full_name,
        "total_commits_fetched": len(commits),
        "new_commits_synced": new_commits,
        "duplicate_commits_skipped": duplicate_commits,
        "synced_commit_shas": synced,
    }

def get_stored_repository_commits(
    repository_id: int,
    db: Session
):
    repository = (
        db.query(GitHubRepository)
        .filter(
            GitHubRepository.id == repository_id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found."
        )
    commits = (
        db.query(Commit)
        .filter(
            Commit.repository_id == repository.id
        )
        .order_by(Commit.committed_at.desc())
        .all()
    )

    return [
    {
        "sha": commit.sha,
        "message": commit.message,
        "author_name": commit.author_name,
        "author_email": commit.author_email,
        "committed_at": commit.committed_at,
    }
    for commit in commits
]

def get_commit_by_id(
    commit_id: int,
    db: Session
):
    """
    Retrieve a specific commit from PostgreSQL.
    """

    commit = (
        db.query(Commit)
        .filter(
            Commit.id == commit_id
        )
        .first()
    )

    if not commit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commit not found."
        )

    return {
        "id": commit.id,
        "sha": commit.sha,
        "message": commit.message,
        "author_name": commit.author_name,
        "author_email": commit.author_email,
        "committed_at": commit.committed_at,
        "repository_id": commit.repository_id
    }

def get_synced_repositories(
    db: Session
):
    repositories = db.query(GitHubRepository).all()

    return [
        {
            "id": repo.id,
            "repo_name": repo.repo_name,
            "full_name": repo.full_name,
            "repo_url": repo.repo_url,
            "owner_name": repo.owner_name,
            "project_id": repo.project_id,
            "private": repo.private,
            "default_branch": repo.default_branch,
            "language": repo.language,
            "stars": repo.stars,
            "forks": repo.forks,
            "connected_at": repo.connected_at
        }
        for repo in repositories
    ]