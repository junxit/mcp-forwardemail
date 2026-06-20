"""Contact (CardDAV) tools for ForwardEmail MCP.

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
        name="contacts_list",
        description="List contacts for an alias (CardDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "page": {"type": "integer", "description": "Page number (1-indexed)"},
                "limit": {
                    "type": "integer",
                    "description": "Results per page (default 100, max 10000)",
                },
            },
            "required": ["alias_username", "alias_password"],
        },
    ),
    Tool(
        name="contact_create",
        description="Create a contact for an alias (CardDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "content": {
                    "type": "string",
                    "description": "Raw vCard content (generated if omitted)",
                },
                "full_name": {"type": "string", "description": "Contact full name"},
                "contact_id": {"type": "string", "description": "Custom contact id"},
                "uid": {"type": "string", "description": "Custom UID"},
                "emails": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of {value, type} email objects",
                },
                "phone_numbers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of {value, type} phone objects",
                },
                "addresses": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of address objects (street, city, state, ...)",
                },
                "is_group": {
                    "type": "boolean",
                    "description": "Whether the contact represents a group",
                },
            },
            "required": ["alias_username", "alias_password"],
        },
    ),
    Tool(
        name="contact_get",
        description="Get a specific contact for an alias (CardDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "contact_id": {"type": "string", "description": "Contact ID"},
            },
            "required": ["alias_username", "alias_password", "contact_id"],
        },
    ),
    Tool(
        name="contact_update",
        description="Update a contact for an alias (CardDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "contact_id": {"type": "string", "description": "Contact ID"},
                "content": {"type": "string", "description": "Raw vCard content"},
                "full_name": {"type": "string", "description": "Contact full name"},
                "emails": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of {value, type} email objects",
                },
                "phone_numbers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of {value, type} phone objects",
                },
                "addresses": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of address objects",
                },
                "is_group": {
                    "type": "boolean",
                    "description": "Whether the contact represents a group",
                },
            },
            "required": ["alias_username", "alias_password", "contact_id"],
        },
    ),
    Tool(
        name="contact_delete",
        description="Delete a contact for an alias (CardDAV). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "contact_id": {"type": "string", "description": "Contact ID"},
            },
            "required": ["alias_username", "alias_password", "contact_id"],
        },
    ),
]


async def handle_contacts_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle contacts_list tool."""
    result, pagination = await client.list_contacts(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        page=args.get("page"),
        limit=args.get("limit"),
    )
    response = {"contacts": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_contact_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle contact_create tool."""
    result = await client.create_contact(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        content=args.get("content"),
        full_name=args.get("full_name"),
        contact_id=args.get("contact_id"),
        uid=args.get("uid"),
        emails=args.get("emails"),
        phone_numbers=args.get("phone_numbers"),
        addresses=args.get("addresses"),
        is_group=args.get("is_group"),
    )
    return json.dumps(result, indent=2)


async def handle_contact_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle contact_get tool."""
    result = await client.get_contact(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        contact_id=args["contact_id"],
    )
    return json.dumps(result, indent=2)


async def handle_contact_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle contact_update tool."""
    result = await client.update_contact(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        contact_id=args["contact_id"],
        content=args.get("content"),
        full_name=args.get("full_name"),
        emails=args.get("emails"),
        phone_numbers=args.get("phone_numbers"),
        addresses=args.get("addresses"),
        is_group=args.get("is_group"),
    )
    return json.dumps(result, indent=2)


async def handle_contact_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle contact_delete tool."""
    result = await client.delete_contact(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        contact_id=args["contact_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "contacts_list": handle_contacts_list,
    "contact_create": handle_contact_create,
    "contact_get": handle_contact_get,
    "contact_update": handle_contact_update,
    "contact_delete": handle_contact_delete,
}
