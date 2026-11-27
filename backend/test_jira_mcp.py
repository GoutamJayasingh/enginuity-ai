
import asyncio
import json
import sys

from mcp.client.stdio import StdioServerParameters

from app.services.mcp_client_service import (
    connect_to_mcp_server,
    execute_mcp_tool,
)


def parse_result(result, operation):

    if result.is_error:
        raise RuntimeError(
            f"{operation} MCP execution failed."
        )

    if not result.content:
        raise RuntimeError(
            f"{operation} returned no response."
        )

    response = json.loads(result.content[0].text)

    print(f"\n{operation.upper()} RESULT")
    print("=" * 40)
    print(json.dumps(response, indent=4))

    if not response.get("success"):
        raise RuntimeError(
            f"{operation} failed: {response.get('message')}"
        )

    return response


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
    )

    async with connect_to_mcp_server(
        server_params
    ) as session:

        # 1. Retrieve Jira projects
        projects_result = await execute_mcp_tool(
            session=session,
            tool_name="get_jira_projects_mcp",
            arguments={},
        )

        projects = parse_result(
            projects_result,
            "Jira Project Retrieval",
        )

        # 2. Retrieve Jira issues
        issues_result = await execute_mcp_tool(
            session=session,
            tool_name="get_jira_issues_mcp",
            arguments={
                "project_key": "SCRUM",
                "max_results": 50,
            },
        )

        parse_result(
            issues_result,
            "Jira Issue Retrieval",
        )

        # 3. Retrieve Jira sprints
        sprints_result = await execute_mcp_tool(
            session=session,
            tool_name="get_jira_sprints_mcp",
            arguments={
                "board_id": 1,
                "max_results": 50,
            },
        )

        sprints = parse_result(
            sprints_result,
            "Jira Sprint Retrieval",
        )

        # 4. Retrieve issues from a sprint
        sprint_issues_result = await execute_mcp_tool(
            session=session,
            tool_name="get_jira_sprint_issues_mcp",
            arguments={
                "sprint_id": 2,
                "max_results": 50,
            },
        )

        parse_result(
            sprint_issues_result,
            "Jira Sprint Issue Retrieval",
        )

        print("\nALL JIRA MCP TESTS COMPLETED")


if __name__ == "__main__":
    asyncio.run(main())
