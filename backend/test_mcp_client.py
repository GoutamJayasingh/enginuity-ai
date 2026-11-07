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
            tool_name="check_google_calendar_availability",
            arguments={
                "time_min": "2026-11-10T09:00:00+05:30",
                "time_max": "2026-11-10T18:00:00+05:30",
            },
        )

        print("\nGOOGLE CALENDAR AVAILABILITY MCP RESULT")
        print("=======================================")

        if result.content:
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())