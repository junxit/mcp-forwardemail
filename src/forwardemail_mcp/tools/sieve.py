"""Domain-scoped Sieve filtering tools for ForwardEmail MCP.

These tools manage server-side Sieve email-filtering scripts for an alias and
authenticate with the account API key (not alias credentials).
"""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="domain_sieve_list",
        description="List Sieve filtering scripts for an alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
            },
            "required": ["domain", "alias_id"],
        },
    ),
    Tool(
        name="domain_sieve_create",
        description="Create a Sieve filtering script for an alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "name": {
                    "type": "string",
                    "description": "Script name",
                },
                "content": {
                    "type": "string",
                    "description": "Sieve script content (RFC 5228)",
                },
                "is_active": {
                    "type": "boolean",
                    "description": "Whether the script is active",
                },
                "priority": {
                    "type": "integer",
                    "description": "Script priority (lower runs first)",
                },
            },
            "required": ["domain", "alias_id", "name", "content"],
        },
    ),
    Tool(
        name="domain_sieve_get",
        description="Get a specific Sieve filtering script for an alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "script_id": {
                    "type": "string",
                    "description": "Sieve script ID or name",
                },
            },
            "required": ["domain", "alias_id", "script_id"],
        },
    ),
    Tool(
        name="domain_sieve_update",
        description="Update a Sieve filtering script for an alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "script_id": {
                    "type": "string",
                    "description": "Sieve script ID or name",
                },
                "content": {
                    "type": "string",
                    "description": "New Sieve script content",
                },
                "description": {
                    "type": "string",
                    "description": "New description",
                },
                "activate": {
                    "type": "boolean",
                    "description": "Whether to activate the script after updating",
                },
            },
            "required": ["domain", "alias_id", "script_id"],
        },
    ),
    Tool(
        name="domain_sieve_delete",
        description="Delete a Sieve filtering script for an alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "script_id": {
                    "type": "string",
                    "description": "Sieve script ID or name",
                },
            },
            "required": ["domain", "alias_id", "script_id"],
        },
    ),
    Tool(
        name="domain_sieve_activate",
        description="Activate a Sieve filtering script for an alias (only one can be active).",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "script_id": {
                    "type": "string",
                    "description": "Sieve script ID or name",
                },
            },
            "required": ["domain", "alias_id", "script_id"],
        },
    ),
]


async def handle_domain_sieve_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_sieve_list tool."""
    result = await client.list_domain_sieve(
        domain=args["domain"],
        alias_id=args["alias_id"],
    )
    return json.dumps({"scripts": result}, indent=2)


async def handle_domain_sieve_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_sieve_create tool."""
    result = await client.create_domain_sieve(
        domain=args["domain"],
        alias_id=args["alias_id"],
        name=args["name"],
        content=args["content"],
        is_active=args.get("is_active"),
        priority=args.get("priority"),
    )
    return json.dumps(result, indent=2)


async def handle_domain_sieve_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_sieve_get tool."""
    result = await client.get_domain_sieve(
        domain=args["domain"],
        alias_id=args["alias_id"],
        script_id=args["script_id"],
    )
    return json.dumps(result, indent=2)


async def handle_domain_sieve_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_sieve_update tool."""
    result = await client.update_domain_sieve(
        domain=args["domain"],
        alias_id=args["alias_id"],
        script_id=args["script_id"],
        content=args.get("content"),
        description=args.get("description"),
        activate=args.get("activate"),
    )
    return json.dumps(result, indent=2)


async def handle_domain_sieve_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_sieve_delete tool."""
    result = await client.delete_domain_sieve(
        domain=args["domain"],
        alias_id=args["alias_id"],
        script_id=args["script_id"],
    )
    return json.dumps(result, indent=2)


async def handle_domain_sieve_activate(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_sieve_activate tool."""
    result = await client.activate_domain_sieve(
        domain=args["domain"],
        alias_id=args["alias_id"],
        script_id=args["script_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "domain_sieve_list": handle_domain_sieve_list,
    "domain_sieve_create": handle_domain_sieve_create,
    "domain_sieve_get": handle_domain_sieve_get,
    "domain_sieve_update": handle_domain_sieve_update,
    "domain_sieve_delete": handle_domain_sieve_delete,
    "domain_sieve_activate": handle_domain_sieve_activate,
}
