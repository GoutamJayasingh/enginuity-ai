from app.db.session import SessionLocal
from app.models.github_repository import GitHubRepository
from app.services.github_service import sync_repositories

db = SessionLocal()

try:
    synced = sync_repositories(db)

    print("Repository Sync Completed!\n")

    if synced:
        print("New repositories added:")
        for repo in synced:
            print(f" - {repo}")
    else:
        print("No new repositories to sync.")

    print("\nRepositories currently in PostgreSQL:\n")

    repositories = db.query(GitHubRepository).all()

    for repo in repositories:
        print(
            f"{repo.repo_name} "
            f"({repo.full_name}) "
            f"[{repo.default_branch}]"
        )

finally:
    db.close()