"""Account management tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="account_get",
        description="Retrieve your ForwardEmail account information including email, plan, and settings.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="account_create",
        description="Create a new ForwardEmail account.",
        inputSchema={
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email address for the new account",
                },
                "password": {
                    "type": "string",
                    "description": "Password for the new account (optional)",
                },
            },
            "required": ["email"],
        },
    ),
    Tool(
        name="account_update",
        description="Update your ForwardEmail account information.",
        inputSchema={
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "New email address",
                },
                "given_name": {
                    "type": "string",
                    "description": "First name",
                },
                "family_name": {
                    "type": "string",
                    "description": "Last name",
                },
                "avatar_url": {
                    "type": "string",
                    "description": "URL to avatar image",
                },
                "default_forwarding_address": {
                    "type": "string",
                    "description": (
                        "Default forwarding address for the account; "
                        "pass an empty string to clear it"
                    ),
                },
            },
            "required": [],
        },
    ),
]


async def handle_account_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle account_get tool."""
    result = await client.get_account()
    return json.dumps(result, indent=2)


async def handle_account_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle account_create tool."""
    result = await client.create_account(
        email=args["email"],
        password=args.get("password"),
    )
    return json.dumps(result, indent=2)


async def handle_account_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle account_update tool."""
    result = await client.update_account(
        email=args.get("email"),
        given_name=args.get("given_name"),
        family_name=args.get("family_name"),
        avatar_url=args.get("avatar_url"),
        default_forwarding_address=args.get("default_forwarding_address"),
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "account_get": handle_account_get,
    "account_create": handle_account_create,
    "account_update": handle_account_update,
}
