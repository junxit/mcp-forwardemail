"""Folder (IMAP) tools for ForwardEmail MCP.

These tools authenticate with ALIAS credentials: alias_username (the full alias
email) and alias_password (generated via the alias_generate_password tool), not
the account API key.
"""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient

_ALIAS_CREDS = {
    "alias_username": {
        "type": "string",
        "description": "Full alias email used as the auth username (e.g. me@example.com)",
    },
    "alias_password": {
        "type": "string",
        "description": "Alias password from the alias_generate_password tool",
    },
}


TOOLS = [
    Tool(
        name="folders_list",
        description="List folders for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "page": {"type": "integer", "description": "Page number (1-indexed)"},
                "limit": {
                    "type": "integer",
                    "description": "Results per page (default 25, max 100)",
                },
                "subscribed": {
                    "type": "boolean",
                    "description": "Filter by subscription status",
                },
            },
            "required": ["alias_username", "alias_password"],
        },
    ),
    Tool(
        name="folder_create",
        description="Create a folder for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "path": {
                    "type": "string",
                    "description": "Folder path (nested like 'INBOX/Sub' auto-creates parents)",
                },
            },
            "required": ["alias_username", "alias_password", "path"],
        },
    ),
    Tool(
        name="folder_get",
        description="Get a specific folder for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "folder_id": {"type": "string", "description": "Folder ID or path"},
            },
            "required": ["alias_username", "alias_password", "folder_id"],
        },
    ),
    Tool(
        name="folder_update",
        description="Rename a folder for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "folder_id": {"type": "string", "description": "Folder ID or path"},
                "path": {"type": "string", "description": "New folder path"},
            },
            "required": ["alias_username", "alias_password", "folder_id", "path"],
        },
    ),
    Tool(
        name="folder_delete",
        description="Delete a folder and its messages for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "folder_id": {"type": "string", "description": "Folder ID or path"},
            },
            "required": ["alias_username", "alias_password", "folder_id"],
        },
    ),
]


async def handle_folders_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle folders_list tool."""
    result, pagination = await client.list_folders(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        page=args.get("page"),
        limit=args.get("limit"),
        subscribed=args.get("subscribed"),
    )
    response = {"folders": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_folder_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle folder_create tool."""
    result = await client.create_folder(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        path=args["path"],
    )
    return json.dumps(result, indent=2)


async def handle_folder_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle folder_get tool."""
    result = await client.get_folder(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        folder_id=args["folder_id"],
    )
    return json.dumps(result, indent=2)


async def handle_folder_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle folder_update tool."""
    result = await client.update_folder(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        folder_id=args["folder_id"],
        path=args["path"],
    )
    return json.dumps(result, indent=2)


async def handle_folder_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle folder_delete tool."""
    result = await client.delete_folder(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        folder_id=args["folder_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "folders_list": handle_folders_list,
    "folder_create": handle_folder_create,
    "folder_get": handle_folder_get,
    "folder_update": handle_folder_update,
    "folder_delete": handle_folder_delete,
}
