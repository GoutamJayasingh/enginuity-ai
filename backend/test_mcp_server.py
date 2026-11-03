from mcp.server.mcpserver import MCPServer


server = MCPServer(
    name="enginuity-test-server",
    version="1.0.0",
)


@server.tool()
def add_numbers(a: int, b: int) -> str:
    """Add two numbers and return their sum."""
    return str(a + b)


if __name__ == "__main__":
    server.run(transport="stdio")