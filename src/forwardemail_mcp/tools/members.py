"""Member management tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="member_update",
        description="Update a domain member's role.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "member_id": {
                    "type": "string",
                    "description": "Member ID",
                },
                "group": {
                    "type": "string",
                    "description": "New role: 'admin' or 'user'",
                    "enum": ["admin", "user"],
                },
            },
            "required": ["domain", "member_id", "group"],
        },
    ),
    Tool(
        name="member_delete",
        description="Remove a member from a domain.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "member_id": {
                    "type": "string",
                    "description": "Member ID to remove",
                },
            },
            "required": ["domain", "member_id"],
        },
    ),
]


async def handle_member_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle member_update tool."""
    result = await client.update_member(
        domain=args["domain"],
        member_id=args["member_id"],
        group=args["group"],
    )
    return json.dumps(result, indent=2)


async def handle_member_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle member_delete tool."""
    result = await client.delete_member(
        domain=args["domain"],
        member_id=args["member_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "member_update": handle_member_update,
    "member_delete": handle_member_delete,
}
