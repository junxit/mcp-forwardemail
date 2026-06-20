"""Calendar (CalDAV) tools for ForwardEmail MCP.

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
        name="calendars_list",
        description="List calendars for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "page": {"type": "integer", "description": "Page number (1-indexed)"},
                "limit": {
                    "type": "integer",
                    "description": "Results per page (default 25, max 100)",
                },
            },
            "required": ["alias_username", "alias_password"],
        },
    ),
    Tool(
        name="calendar_create",
        description="Create a calendar for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "name": {"type": "string", "description": "Calendar name"},
                "calendar_id": {"type": "string", "description": "Custom calendar id"},
                "description": {"type": "string", "description": "Calendar description"},
                "color": {"type": "string", "description": "Calendar color (hex)"},
                "timezone": {"type": "string", "description": "Calendar timezone"},
                "order": {"type": "integer", "description": "Sort order"},
            },
            "required": ["alias_username", "alias_password", "name"],
        },
    ),
    Tool(
        name="calendar_get",
        description="Get a specific calendar for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "calendar_id": {"type": "string", "description": "Calendar ID"},
            },
            "required": ["alias_username", "alias_password", "calendar_id"],
        },
    ),
    Tool(
        name="calendar_update",
        description="Update a calendar for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "calendar_id": {"type": "string", "description": "Calendar ID"},
                "name": {"type": "string", "description": "New calendar name"},
                "description": {"type": "string", "description": "New description"},
                "color": {"type": "string", "description": "New color (hex)"},
                "timezone": {"type": "string", "description": "New timezone"},
                "order": {"type": "integer", "description": "New sort order"},
            },
            "required": ["alias_username", "alias_password", "calendar_id"],
        },
    ),
    Tool(
        name="calendar_delete",
        description="Delete a calendar and its events for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "calendar_id": {"type": "string", "description": "Calendar ID"},
            },
            "required": ["alias_username", "alias_password", "calendar_id"],
        },
    ),
]


async def handle_calendars_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendars_list tool."""
    result, pagination = await client.list_calendars(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        page=args.get("page"),
        limit=args.get("limit"),
    )
    response = {"calendars": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_calendar_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_create tool."""
    result = await client.create_calendar(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        name=args["name"],
        calendar_id=args.get("calendar_id"),
        description=args.get("description"),
        color=args.get("color"),
        timezone=args.get("timezone"),
        order=args.get("order"),
    )
    return json.dumps(result, indent=2)


async def handle_calendar_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_get tool."""
    result = await client.get_calendar(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        calendar_id=args["calendar_id"],
    )
    return json.dumps(result, indent=2)


async def handle_calendar_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_update tool."""
    result = await client.update_calendar(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        calendar_id=args["calendar_id"],
        name=args.get("name"),
        description=args.get("description"),
        color=args.get("color"),
        timezone=args.get("timezone"),
        order=args.get("order"),
    )
    return json.dumps(result, indent=2)


async def handle_calendar_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_delete tool."""
    result = await client.delete_calendar(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        calendar_id=args["calendar_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "calendars_list": handle_calendars_list,
    "calendar_create": handle_calendar_create,
    "calendar_get": handle_calendar_get,
    "calendar_update": handle_calendar_update,
    "calendar_delete": handle_calendar_delete,
}
