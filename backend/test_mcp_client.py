import asyncio
import sys
from pathlib import Path

from mcp.client.stdio import StdioServerParameters

from app.services.mcp_client_service import (
    connect_to_mcp_server,
)

from app.services.mcp_client_service import (
    connect_to_mcp_server,
    discover_mcp_tools,
    execute_mcp_tool,
)

async def main():

    server_script = (
        Path(__file__).parent
        / "app"
        / "mcp"
        / "server.py"
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
    )

    async with connect_to_mcp_server(
        server_params
    ) as session:

        discovered_tools = await discover_mcp_tools(session)

        print("\nAVAILABLE MCP TOOLS")
        print("===================")

        for tool in discovered_tools:
            print(tool)

        result = await execute_mcp_tool(
            session=session,
            tool_name="get_jira_sprint_issues_mcp",
            arguments={
                "sprint_id": 2,
                "max_results": 50,
            },
        )

        print("\nJIRA SPRINT ISSUES MCP RESULT")
        print("=============================")

        if result.content:
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())