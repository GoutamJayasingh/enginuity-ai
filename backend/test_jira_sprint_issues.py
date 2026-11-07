from pprint import pprint

from app.services.jira_service import (
    get_jira_sprint_issues,
)


result = get_jira_sprint_issues(
    sprint_id=2,
    max_results=50,
)

pprint(result)