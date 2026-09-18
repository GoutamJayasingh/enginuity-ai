import os

from dotenv import load_dotenv
from github import Github

from fastapi import HTTPException, status

from app.models.user import User

from collections import defaultdict

from app.models.pull_request import PullRequest

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

def get_repository_analytics(
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

    total_commits = (
        db.query(Commit)
        .filter(
            Commit.repository_id == repository.id
        )
        .count()
    )

    total_contributors = (
        db.query(Commit.author_name)
        .filter(
            Commit.repository_id == repository.id
        )
        .distinct()
        .count()
    )

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "total_commits": total_commits,
        "total_contributors": total_contributors,
        "stars": repository.stars,
        "forks": repository.forks,
        "language": repository.language
    }

def get_commit_analytics(
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
        .order_by(
            Commit.committed_at.desc()
        )
        .all()
    )

    if not commits:
        return {
            "repository_id": repository.id,
            "repository_name": repository.repo_name,
            "total_commits": 0,
            "recent_commits": [],
            "commits_by_author": {}
        }

    commits_by_author = {}

    for commit in commits:

        author = commit.author_name or "Unknown"

        if author not in commits_by_author:
            commits_by_author[author] = 0

        commits_by_author[author] += 1

    recent_commits = [
        {
            "sha": commit.sha,
            "message": commit.message,
            "author_name": commit.author_name,
            "committed_at": commit.committed_at
        }
        for commit in commits[:10]
    ]

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "total_commits": len(commits),
        "recent_commits": recent_commits,
        "commits_by_author": commits_by_author
    }

def get_contributor_analytics(
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
        .all()
    )

    contributor_commits = {}

    for commit in commits:

        author = commit.author_name or "Unknown"

        if author not in contributor_commits:
            contributor_commits[author] = 0

        contributor_commits[author] += 1

    total_commits = len(commits)

    contributors = []

    for author, commit_count in contributor_commits.items():

        percentage = (
            (commit_count / total_commits) * 100
            if total_commits > 0
            else 0
        )

        contributors.append({
            "author_name": author,
            "commit_count": commit_count,
            "commit_percentage": round(percentage, 2)
        })

    contributors.sort(
        key=lambda contributor: contributor["commit_count"],
        reverse=True
    )

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "total_commits": total_commits,
        "total_contributors": len(contributors),
        "contributors": contributors
    }

def get_commit_activity(
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
        .order_by(
            Commit.committed_at.asc()
        )
        .all()
    )

    activity = defaultdict(int)

    for commit in commits:

        if commit.committed_at:
            date = commit.committed_at.date().isoformat()
            activity[date] += 1

    commit_activity = [
        {
            "date": date,
            "commit_count": count
        }
        for date, count in sorted(activity.items())
    ]

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "total_commits": len(commits),
        "commit_activity": commit_activity
    }

def get_github_analytics_summary(
    repository_id: int,
    db: Session
):
    repository_analytics = get_repository_analytics(
        repository_id=repository_id,
        db=db
    )

    commit_analytics = get_commit_analytics(
        repository_id=repository_id,
        db=db
    )

    contributor_analytics = get_contributor_analytics(
        repository_id=repository_id,
        db=db
    )

    commit_activity = get_commit_activity(
        repository_id=repository_id,
        db=db
    )

    return {
        "repository": repository_analytics,
        "commits": commit_analytics,
        "contributors": contributor_analytics,
        "activity": commit_activity
    }

def sync_pull_requests(
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

    github_repository = github.get_repo(
        repository.full_name
    )

    pull_requests = github_repository.get_pulls(
        state="all",
        sort="updated",
        direction="desc"
    )

    new_pull_requests = 0
    updated_pull_requests = 0

    for pull_request in pull_requests:

        existing_pull_request = (
            db.query(PullRequest)
            .filter(
                PullRequest.github_id == pull_request.id
            )
            .first()
        )

        pull_request_data = {
            "github_id": pull_request.id,
            "number": pull_request.number,
            "title": pull_request.title,
            "description": pull_request.body,
            "state": pull_request.state,
            "author_name": (
                pull_request.user.login
                if pull_request.user
                else None
            ),
            "author_url": (
                pull_request.user.html_url
                if pull_request.user
                else None
            ),
            "source_branch": pull_request.head.ref,
            "target_branch": pull_request.base.ref,
            "created_at": pull_request.created_at,
            "updated_at": pull_request.updated_at,
            "merged_at": pull_request.merged_at,
            "merged": pull_request.merged_at is not None,
            "repository_id": repository.id
        }

        if existing_pull_request:

            for field, value in pull_request_data.items():
                setattr(
                    existing_pull_request,
                    field,
                    value
                )

            updated_pull_requests += 1

        else:

            new_pull_request = PullRequest(
                **pull_request_data
            )

            db.add(new_pull_request)

            new_pull_requests += 1

    db.commit()

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "total_pull_requests": (
            new_pull_requests + updated_pull_requests
        ),
        "new_pull_requests": new_pull_requests,
        "updated_pull_requests": updated_pull_requests
    }

def get_pull_request_analytics(
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

    pull_requests = (
        db.query(PullRequest)
        .filter(
            PullRequest.repository_id == repository.id
        )
        .all()
    )

    total_pull_requests = len(pull_requests)

    open_pull_requests = 0
    closed_pull_requests = 0
    merged_pull_requests = 0
    unmerged_pull_requests = 0

    contributors = set()

    for pull_request in pull_requests:

        if pull_request.state == "open":
            open_pull_requests += 1

        elif pull_request.state == "closed":
            closed_pull_requests += 1

        if pull_request.merged:
            merged_pull_requests += 1
        else:
            unmerged_pull_requests += 1

        if pull_request.author_name:
            contributors.add(
                pull_request.author_name
            )

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "total_pull_requests": total_pull_requests,
        "open_pull_requests": open_pull_requests,
        "closed_pull_requests": closed_pull_requests,
        "merged_pull_requests": merged_pull_requests,
        "unmerged_pull_requests": unmerged_pull_requests,
        "total_contributors": len(contributors)
    }

def get_branch_analytics(
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

    github_repository = github.get_repo(
        repository.full_name
    )

    branches = github_repository.get_branches()

    branch_data = []

    protected_branches = 0

    for branch in branches:

        is_protected = branch.protected

        if is_protected:
            protected_branches += 1

        branch_data.append({
            "name": branch.name,
            "protected": is_protected
        })

    return {
        "repository_id": repository.id,
        "repository_name": repository.repo_name,
        "default_branch": repository.default_branch,
        "total_branches": len(branch_data),
        "protected_branches": protected_branches,
        "branches": branch_data
    }