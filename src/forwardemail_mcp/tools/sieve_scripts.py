"""Sieve script tools (alias-credential auth) for ForwardEmail MCP.

These manage server-side Sieve filtering scripts using ALIAS credentials:
alias_username (the full alias email) and alias_password (generated via the
alias_generate_password tool). This is the alias-auth counterpart to the
account-API-key domain_sieve_* tools.
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
        name="sieve_scripts_list",
        description="List Sieve scripts for an alias. Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {**_ALIAS_CREDS},
            "required": ["alias_username", "alias_password"],
        },
    ),
    Tool(
        name="sieve_script_create",
        description="Create a Sieve script for an alias. Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "name": {"type": "string", "description": "Script name"},
                "content": {
                    "type": "string",
                    "description": "Sieve script content (RFC 5228)",
                },
                "description": {"type": "string", "description": "Script description"},
            },
            "required": ["alias_username", "alias_password", "name", "content"],
        },
    ),
    Tool(
        name="sieve_script_get",
        description="Get a specific Sieve script for an alias. Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "script_id": {"type": "string", "description": "Sieve script ID or name"},
            },
            "required": ["alias_username", "alias_password", "script_id"],
        },
    ),
    Tool(
        name="sieve_script_update",
        description="Update a Sieve script for an alias. Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "script_id": {"type": "string", "description": "Sieve script ID or name"},
                "content": {"type": "string", "description": "New Sieve script content"},
                "description": {"type": "string", "description": "New description"},
                "activate": {
                    "type": "boolean",
                    "description": "Whether to activate the script after updating",
                },
            },
            "required": ["alias_username", "alias_password", "script_id"],
        },
    ),
    Tool(
        name="sieve_script_delete",
        description="Delete a Sieve script for an alias (cannot delete the active script). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "script_id": {"type": "string", "description": "Sieve script ID or name"},
            },
            "required": ["alias_username", "alias_password", "script_id"],
        },
    ),
    Tool(
        name="sieve_script_activate",
        description="Activate a Sieve script for an alias (only one can be active). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "script_id": {"type": "string", "description": "Sieve script ID or name"},
            },
            "required": ["alias_username", "alias_password", "script_id"],
        },
    ),
]


async def handle_sieve_scripts_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle sieve_scripts_list tool."""
    result = await client.list_sieve_scripts(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
    )
    return json.dumps({"scripts": result}, indent=2)


async def handle_sieve_script_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle sieve_script_create tool."""
    result = await client.create_sieve_script(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        name=args["name"],
        content=args["content"],
        description=args.get("description"),
    )
    return json.dumps(result, indent=2)


async def handle_sieve_script_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle sieve_script_get tool."""
    result = await client.get_sieve_script(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        script_id=args["script_id"],
    )
    return json.dumps(result, indent=2)


async def handle_sieve_script_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle sieve_script_update tool."""
    result = await client.update_sieve_script(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        script_id=args["script_id"],
        content=args.get("content"),
        description=args.get("description"),
        activate=args.get("activate"),
    )
    return json.dumps(result, indent=2)


async def handle_sieve_script_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle sieve_script_delete tool."""
    result = await client.delete_sieve_script(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        script_id=args["script_id"],
    )
    return json.dumps(result, indent=2)


async def handle_sieve_script_activate(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle sieve_script_activate tool."""
    result = await client.activate_sieve_script(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        script_id=args["script_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "sieve_scripts_list": handle_sieve_scripts_list,
    "sieve_script_create": handle_sieve_script_create,
    "sieve_script_get": handle_sieve_script_get,
    "sieve_script_update": handle_sieve_script_update,
    "sieve_script_delete": handle_sieve_script_delete,
    "sieve_script_activate": handle_sieve_script_activate,
}
