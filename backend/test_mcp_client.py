
import asyncio
import json
import sys

from mcp.client.stdio import StdioServerParameters

from app.services.mcp_client_service import (
    connect_to_mcp_server,
    discover_mcp_tools,
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

        # STEP 1: Discover MCP tools

        tools = await discover_mcp_tools(session)

        print("\nAVAILABLE MCP TOOLS")
        print("===================")

        for tool in tools:
            print(tool["name"])

        # STEP 2: Retrieve upcoming events

        events_result = await execute_mcp_tool(
            session=session,
            tool_name="get_upcoming_calendar_events",
            arguments={
                "max_results": 10,
            },
        )

        parse_result(
            events_result,
            "Event Retrieval",
        )

        # STEP 3: Check calendar availability

        availability_result = await execute_mcp_tool(
            session=session,
            tool_name="check_google_calendar_availability",
            arguments={
                "time_min": "2026-11-12T09:00:00+05:30",
                "time_max": "2026-11-12T18:00:00+05:30",
            },
        )

        parse_result(
            availability_result,
            "Availability Checking",
        )

        # STEP 4: Create a temporary event

        create_result = await execute_mcp_tool(
            session=session,
            tool_name="create_google_calendar_event",
            arguments={
                "summary": "Enginuity-AI Response Test",
                "start_time": "2026-11-12T11:00:00+05:30",
                "end_time": "2026-11-12T11:30:00+05:30",
                "description": "Testing standardized MCP responses",
                "location": "Online",
            },
        )

        created_event = parse_result(
            create_result,
            "Event Creation",
        )

        event_id = created_event["data"]["event_id"]

        # STEP 5: Update the temporary event

        update_result = await execute_mcp_tool(
            session=session,
            tool_name="update_google_calendar_event",
            arguments={
                "event_id": event_id,
                "summary": "Enginuity-AI Updated Response Test",
                "description": "MCP response standardization verified",
            },
        )

        parse_result(
            update_result,
            "Event Update",
        )

        # STEP 6: Delete the temporary event

        delete_result = await execute_mcp_tool(
            session=session,
            tool_name="delete_google_calendar_event",
            arguments={
                "event_id": event_id,
            },
        )

        parse_result(
            delete_result,
            "Event Deletion",
        )

        print("\nALL CALENDAR MCP TESTS COMPLETED")


if __name__ == "__main__":
    asyncio.run(main())
