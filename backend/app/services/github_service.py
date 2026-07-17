import os

from dotenv import load_dotenv
from github import Github

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