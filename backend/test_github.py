from pprint import pprint

from app.services.github_service import get_user_repositories

repositories = get_user_repositories()

print(f"Found {len(repositories)} repositories\n")

for repository in repositories:
    pprint(repository)
    print("-" * 60)