"""ForwardEmail MCP Server.

This module provides the main MCP server entry point for ForwardEmail API access.
It registers all tools and handles requests from MCP clients like Claude Desktop.

Typical usage example:

    # Run via command line
    $ FORWARDEMAIL_API_KEY="your_key" forwardemail-mcp

    # Or import and run programmatically
    from forwardemail_mcp.server import main
    main()

Attributes:
    ALL_TOOLS: List of all registered MCP tools.
    TOOL_HANDLERS: Dict mapping tool names to handler functions.
"""

import os
import sys
import logging
import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import ForwardEmailClient
from .tools import account, domains, aliases, emails, invites, members, logs, encrypt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("forwardemail-mcp")


def get_api_key() -> str:
    """Get API key from environment variable.

    Returns:
        The ForwardEmail API key.

    Raises:
        ValueError: If FORWARDEMAIL_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("FORWARDEMAIL_API_KEY")
    if not api_key:
        raise ValueError(
            "FORWARDEMAIL_API_KEY environment variable is required. "
            "Get your API key from https://forwardemail.net/my-account/security"
        )
    return api_key


# Collect all tools from modules
ALL_TOOLS = [
    *account.TOOLS,
    *domains.TOOLS,
    *aliases.TOOLS,
    *emails.TOOLS,
    *invites.TOOLS,
    *members.TOOLS,
    *logs.TOOLS,
    *encrypt.TOOLS,
]

# Collect all handlers
TOOL_HANDLERS = {
    **account.HANDLERS,
    **domains.HANDLERS,
    **aliases.HANDLERS,
    **emails.HANDLERS,
    **invites.HANDLERS,
    **members.HANDLERS,
    **logs.HANDLERS,
    **encrypt.HANDLERS,
}


async def run_server() -> None:
    """Run the MCP server.

    Initializes the ForwardEmail client and MCP server, registers tool handlers,
    and runs the server using stdio transport.

    Raises:
        SystemExit: If API key is not configured.
    """
    # Validate API key on startup
    try:
        api_key = get_api_key()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Create the MCP server
    server = Server("forwardemail-mcp")

    # Create the API client
    client = ForwardEmailClient(api_key)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools.

        Returns:
            List of Tool objects describing available MCP tools.
        """
        return ALL_TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls.

        Args:
            name: Name of the tool to execute.
            arguments: Dict of arguments to pass to the tool.

        Returns:
            List containing a single TextContent with the tool result.

        Raises:
            ValueError: If tool name is not recognized.
        """
        if name not in TOOL_HANDLERS:
            raise ValueError(f"Unknown tool: {name}")

        handler = TOOL_HANDLERS[name]

        try:
            result = await handler(client, arguments)
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.exception(f"Error executing tool {name}")
            error_msg = str(e)
            # Don't expose full error details that might leak credentials
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = "Authentication failed. Please check your FORWARDEMAIL_API_KEY."
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        logger.info("ForwardEmail MCP server starting...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Main entry point.

    Runs the async MCP server using asyncio.run().
    """
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
