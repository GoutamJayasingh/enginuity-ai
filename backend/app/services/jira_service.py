import os
import requests

from dotenv import load_dotenv

load_dotenv()


def get_jira_current_user():

    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError(
            "Jira credentials are not configured."
        )

    response = requests.get(
        f"{base_url}/rest/api/3/myself",
        auth=(email, api_token),
        headers={
            "Accept": "application/json"
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()

def get_jira_projects():

    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError(
            "Jira credentials are not configured."
        )

    response = requests.get(
        f"{base_url}/rest/api/3/project/search",
        auth=(email, api_token),
        headers={
            "Accept": "application/json"
        },
        params={
            "maxResults": 50
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "total": data.get("total", 0),
        "projects": [
            {
                "id": project.get("id"),
                "key": project.get("key"),
                "name": project.get("name"),
                "project_type": project.get("projectTypeKey"),
                "project_url": project.get("self"),
            }
            for project in data.get("values", [])
        ],
    }

def get_jira_issues(
    project_key: str,
    max_results: int = 50,
):

    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError(
            "Jira credentials are not configured."
        )

    response = requests.get(
        f"{base_url}/rest/api/3/search/jql",
        auth=(email, api_token),
        headers={
            "Accept": "application/json"
        },
        params={
            "jql": f"project = {project_key} ORDER BY created DESC",
            "maxResults": max_results,
            "fields": (
                "summary,status,assignee,priority,"
                "issuetype,created,duedate"
            ),
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    issues = []

    for issue in data.get("issues", []):

        fields = issue.get("fields", {})

        assignee = fields.get("assignee")
        priority = fields.get("priority")
        status = fields.get("status")
        issue_type = fields.get("issuetype")

        issues.append({
            "id": issue.get("id"),
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "issue_type": (
                issue_type.get("name")
                if issue_type else None
            ),
            "status": (
                status.get("name")
                if status else None
            ),
            "assignee": (
                assignee.get("displayName")
                if assignee else None
            ),
            "priority": (
                priority.get("name")
                if priority else None
            ),
            "created": fields.get("created"),
            "due_date": fields.get("duedate"),
        })

    return {
        "project_key": project_key,
        "total": len(issues),
        "issues": issues,
        "is_last": data.get("isLast"),
    }

def get_jira_sprints(
    board_id: int,
    max_results: int = 50,
):

    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError(
            "Jira credentials are not configured."
        )

    response = requests.get(
        f"{base_url}/rest/agile/1.0/board/{board_id}/sprint",
        auth=(email, api_token),
        headers={
            "Accept": "application/json"
        },
        params={
            "maxResults": max_results
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    sprints = []

    for sprint in data.get("values", []):

        sprints.append({
            "id": sprint.get("id"),
            "name": sprint.get("name"),
            "state": sprint.get("state"),
            "start_date": sprint.get("startDate"),
            "end_date": sprint.get("endDate"),
            "created_date": sprint.get("createdDate"),
            "board_id": sprint.get("originBoardId"),
        })

    return {
        "board_id": board_id,
        "total": len(sprints),
        "sprints": sprints,
        "is_last": data.get("isLast"),
    }

def get_jira_sprint_issues(
    sprint_id: int,
    max_results: int = 50,
):
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        raise ValueError(
            "Jira credentials are not configured."
        )

    response = requests.get(
        f"{base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
        auth=(email, api_token),
        headers={
            "Accept": "application/json"
        },
        params={
            "startAt": 0,
            "maxResults": max_results,
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    issues = []

    for issue in data.get("issues", []):
        fields = issue.get("fields", {})

        issue_type = fields.get("issuetype")
        status = fields.get("status")
        assignee = fields.get("assignee")
        priority = fields.get("priority")

        issues.append({
            "id": issue.get("id"),
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "issue_type": (
                issue_type.get("name")
                if issue_type else None
            ),
            "status": (
                status.get("name")
                if status else None
            ),
            "assignee": (
                assignee.get("displayName")
                if assignee else None
            ),
            "priority": (
                priority.get("name")
                if priority else None
            ),
            "created": fields.get("created"),
            "due_date": fields.get("duedate"),
        })

    return {
        "sprint_id": sprint_id,
        "total": data.get("total", 0),
        "issues": issues,
        "is_last": data.get("isLast"),
    }