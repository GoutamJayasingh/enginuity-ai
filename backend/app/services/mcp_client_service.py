from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)


@asynccontextmanager
async def connect_to_mcp_server(
    server_params: StdioServerParameters,
) -> AsyncIterator[ClientSession]:

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            yield session

async def discover_mcp_tools(
    session: ClientSession,
) -> list[dict]:

    tools_result = await session.list_tools()

    discovered_tools = []

    for tool in tools_result.tools:
        discovered_tools.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        })

    return discovered_tools

async def execute_mcp_tool(
    session: ClientSession,
    tool_name: str,
    arguments: dict,
):

    result = await session.call_tool(
        tool_name,
        arguments=arguments,
    )

    return result