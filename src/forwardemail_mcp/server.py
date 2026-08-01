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
from typing import Optional

from mcp.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
)

from .client import ForwardEmailClient
from .tools import (
    account,
    domains,
    aliases,
    emails,
    invites,
    members,
    logs,
    encrypt,
    sieve,
    contacts,
    calendars,
    calendar_events,
    messages,
    folders,
    sieve_scripts,
)

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
    *sieve.TOOLS,
    *contacts.TOOLS,
    *calendars.TOOLS,
    *calendar_events.TOOLS,
    *messages.TOOLS,
    *folders.TOOLS,
    *sieve_scripts.TOOLS,
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
    **sieve.HANDLERS,
    **contacts.HANDLERS,
    **calendars.HANDLERS,
    **calendar_events.HANDLERS,
    **messages.HANDLERS,
    **folders.HANDLERS,
    **sieve_scripts.HANDLERS,
}


def _error_result(text: str) -> CallToolResult:
    """Build an error CallToolResult.

    Args:
        text: Human-readable error message to surface to the client.

    Returns:
        CallToolResult carrying the message and flagged with is_error.
    """
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        is_error=True,
    )


def create_server(client: ForwardEmailClient) -> Server:
    """Build the MCP server bound to a ForwardEmail client.

    Kept separate from run_server so the configured server can be driven
    in-process by tests via the SDK's in-memory client transport.

    Args:
        client: ForwardEmail API client used to execute tool calls.

    Returns:
        Server with the tool-listing and tool-calling handlers wired up.
    """

    async def on_list_tools(
        ctx: ServerRequestContext,
        params: Optional[PaginatedRequestParams],
    ) -> ListToolsResult:
        """List all available tools.

        Args:
            ctx: Per-request server context supplied by the SDK.
            params: Pagination parameters (unused; the full tool set is small
                enough to return in one page).

        Returns:
            ListToolsResult wrapping every registered MCP tool.
        """
        return ListToolsResult(tools=ALL_TOOLS)

    async def on_call_tool(
        ctx: ServerRequestContext,
        params: CallToolRequestParams,
    ) -> CallToolResult:
        """Handle tool calls.

        The SDK does not convert handler exceptions into error results, so every
        failure path must return a CallToolResult explicitly.

        Args:
            ctx: Per-request server context supplied by the SDK.
            params: Tool invocation parameters carrying the name and arguments.

        Returns:
            CallToolResult with the tool output, or an error result flagged with
            is_error if the tool is unknown or raised.
        """
        name = params.name
        arguments = params.arguments or {}

        handler = TOOL_HANDLERS.get(name)
        if handler is None:
            logger.error(f"Unknown tool: {name}")
            return _error_result(f"Unknown tool: {name}")

        try:
            result = await handler(client, arguments)
            return CallToolResult(content=[TextContent(type="text", text=str(result))])
        except Exception as e:
            logger.exception(f"Error executing tool {name}")
            error_msg = str(e)
            # Don't expose full error details that might leak credentials
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = "Authentication failed. Please check your FORWARDEMAIL_API_KEY."
            return _error_result(f"Error: {error_msg}")

    # Handlers are wired via constructor parameters; everything after `name`
    # is keyword-only.
    return Server(
        "forwardemail-mcp",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )


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

    client = ForwardEmailClient(api_key)
    server = create_server(client)

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
