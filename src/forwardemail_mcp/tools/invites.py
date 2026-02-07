"""Invite management tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="invite_accept",
        description="Accept a domain invite that was sent to you.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name to accept invite for",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="invite_create",
        description="Invite a user to join your domain as admin or user.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "email": {
                    "type": "string",
                    "description": "Email address to invite",
                },
                "group": {
                    "type": "string",
                    "description": "Role: 'admin' or 'user'",
                    "enum": ["admin", "user"],
                    "default": "user",
                },
            },
            "required": ["domain", "email"],
        },
    ),
    Tool(
        name="invite_delete",
        description="Remove/cancel a pending domain invite.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the invite to remove",
                },
            },
            "required": ["domain", "email"],
        },
    ),
]


async def handle_invite_accept(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle invite_accept tool."""
    result = await client.accept_invite(args["domain"])
    return json.dumps(result, indent=2)


async def handle_invite_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle invite_create tool."""
    result = await client.create_invite(
        domain=args["domain"],
        email=args["email"],
        group=args.get("group", "user"),
    )
    return json.dumps(result, indent=2)


async def handle_invite_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle invite_delete tool."""
    result = await client.delete_invite(
        domain=args["domain"],
        email=args["email"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "invite_accept": handle_invite_accept,
    "invite_create": handle_invite_create,
    "invite_delete": handle_invite_delete,
}
