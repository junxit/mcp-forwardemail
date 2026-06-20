"""Calendar event (CalDAV) tools for ForwardEmail MCP.

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
        name="calendar_events_list",
        description="List calendar events for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "calendar_id": {"type": "string", "description": "Filter by calendar ID"},
                "start_date": {"type": "string", "description": "ISO date-time lower bound"},
                "end_date": {"type": "string", "description": "ISO date-time upper bound"},
                "include_deleted": {
                    "type": "boolean",
                    "description": "Include soft-deleted events",
                },
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
        name="calendar_event_create",
        description="Create a calendar event for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "calendar_id": {
                    "type": "string",
                    "description": "Calendar ID to add the event to",
                },
                "ical": {
                    "type": "string",
                    "description": "RFC 5545 iCalendar event content",
                },
                "event_id": {"type": "string", "description": "Custom event id"},
            },
            "required": ["alias_username", "alias_password", "calendar_id", "ical"],
        },
    ),
    Tool(
        name="calendar_event_get",
        description="Get a specific calendar event for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "event_id": {"type": "string", "description": "Event ID"},
            },
            "required": ["alias_username", "alias_password", "event_id"],
        },
    ),
    Tool(
        name="calendar_event_update",
        description="Update a calendar event for an alias (CalDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "event_id": {"type": "string", "description": "Event ID"},
                "calendar_id": {
                    "type": "string",
                    "description": "Move the event to another calendar",
                },
                "ical": {
                    "type": "string",
                    "description": "Updated RFC 5545 iCalendar content",
                },
            },
            "required": ["alias_username", "alias_password", "event_id"],
        },
    ),
    Tool(
        name="calendar_event_delete",
        description="Delete a calendar event for an alias (CalDAV, soft delete). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "event_id": {"type": "string", "description": "Event ID"},
            },
            "required": ["alias_username", "alias_password", "event_id"],
        },
    ),
]


async def handle_calendar_events_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_events_list tool."""
    result, pagination = await client.list_calendar_events(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        calendar_id=args.get("calendar_id"),
        start_date=args.get("start_date"),
        end_date=args.get("end_date"),
        include_deleted=args.get("include_deleted"),
        page=args.get("page"),
        limit=args.get("limit"),
    )
    response = {"events": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_calendar_event_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_event_create tool."""
    result = await client.create_calendar_event(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        calendar_id=args["calendar_id"],
        ical=args["ical"],
        event_id=args.get("event_id"),
    )
    return json.dumps(result, indent=2)


async def handle_calendar_event_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_event_get tool."""
    result = await client.get_calendar_event(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        event_id=args["event_id"],
    )
    return json.dumps(result, indent=2)


async def handle_calendar_event_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_event_update tool."""
    result = await client.update_calendar_event(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        event_id=args["event_id"],
        calendar_id=args.get("calendar_id"),
        ical=args.get("ical"),
    )
    return json.dumps(result, indent=2)


async def handle_calendar_event_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle calendar_event_delete tool."""
    result = await client.delete_calendar_event(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        event_id=args["event_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "calendar_events_list": handle_calendar_events_list,
    "calendar_event_create": handle_calendar_event_create,
    "calendar_event_get": handle_calendar_event_get,
    "calendar_event_update": handle_calendar_event_update,
    "calendar_event_delete": handle_calendar_event_delete,
}
