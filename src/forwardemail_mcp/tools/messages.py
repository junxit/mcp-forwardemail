"""Message (IMAP) tools for ForwardEmail MCP.

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

# Curated subset of the ~35 supported search filters, surfaced as first-class
# inputs. Anything else (e.g. is_junk, min_size, headers, "reply-to") can be
# passed through the free-form `filters` object.
_CURATED_FILTERS = [
    "folder",
    "is_unread",
    "is_flagged",
    "subject",
    "from",
    "to",
    "search",
    "since",
    "before",
    "has_attachments",
]


TOOLS = [
    Tool(
        name="messages_list",
        description="List and search messages for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "folder": {"type": "string", "description": "Filter by folder path"},
                "is_unread": {"type": "boolean", "description": "Only unread messages"},
                "is_flagged": {"type": "boolean", "description": "Only flagged messages"},
                "subject": {"type": "string", "description": "Subject search"},
                "from": {"type": "string", "description": "From-header search"},
                "to": {"type": "string", "description": "To-header search"},
                "search": {"type": "string", "description": "Full-text search query"},
                "since": {"type": "string", "description": "ISO date-time lower bound"},
                "before": {"type": "string", "description": "ISO date-time upper bound"},
                "has_attachments": {
                    "type": "boolean",
                    "description": "Only messages with attachments",
                },
                "filters": {
                    "type": "object",
                    "description": (
                        "Additional raw query filters not covered above "
                        "(e.g. is_junk, min_size, max_size, headers, message_id, 'reply-to')"
                    ),
                },
                "lightweight": {
                    "type": "boolean",
                    "description": (
                        "Return metadata-only results. Much faster for list views, but "
                        "the response omits 'nodemailer' and 'raw' and instead carries "
                        "from/to/cc/bcc/reply_to parsed from the headers"
                    ),
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
        name="message_create",
        description="Create/append a message for an alias (IMAP, Nodemailer format). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "from": {"type": "string", "description": "Sender address"},
                "to": {"type": "string", "description": "Recipient(s), comma-separated or array"},
                "cc": {"type": "string", "description": "CC recipient(s)"},
                "bcc": {"type": "string", "description": "BCC recipient(s)"},
                "subject": {"type": "string", "description": "Subject line"},
                "text": {"type": "string", "description": "Plain-text body"},
                "html": {"type": "string", "description": "HTML body"},
                "attachments": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of attachment objects",
                },
                "folder": {"type": "string", "description": "Target folder (default INBOX)"},
                "flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IMAP flags",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels (max 10)",
                },
            },
            "required": ["alias_username", "alias_password"],
        },
    ),
    Tool(
        name="message_get",
        description="Get a specific message for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "message_id": {"type": "string", "description": "Message ID"},
                "eml": {
                    "type": "boolean",
                    "description": "Return the raw RFC822 message instead of JSON",
                },
                "nodemailer": {
                    "type": "boolean",
                    "description": "Include the parsed Nodemailer representation",
                },
                "attachments": {"type": "boolean", "description": "Include attachments"},
                "raw": {"type": "boolean", "description": "Include the raw source"},
            },
            "required": ["alias_username", "alias_password", "message_id"],
        },
    ),
    Tool(
        name="message_update",
        description="Update a message (flags/labels/folder move) for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "message_id": {"type": "string", "description": "Message ID"},
                "flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New IMAP flags",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New labels",
                },
                "folder": {"type": "string", "description": "Move the message to this folder"},
            },
            "required": ["alias_username", "alias_password", "message_id"],
        },
    ),
    Tool(
        name="message_delete",
        description="Permanently delete a message for an alias (IMAP). Requires alias credentials.",
        inputSchema={
            "type": "object",
            "properties": {
                **_ALIAS_CREDS,
                "message_id": {"type": "string", "description": "Message ID"},
            },
            "required": ["alias_username", "alias_password", "message_id"],
        },
    ),
]


async def handle_messages_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle messages_list tool."""
    filters = {k: args[k] for k in _CURATED_FILTERS if k in args}
    filters.update(args.get("filters") or {})
    result, pagination = await client.list_messages(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        page=args.get("page"),
        limit=args.get("limit"),
        lightweight=args.get("lightweight"),
        filters=filters or None,
    )
    response = {"messages": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_message_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle message_create tool."""
    result = await client.create_message(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        from_addr=args.get("from"),
        to=args.get("to"),
        cc=args.get("cc"),
        bcc=args.get("bcc"),
        subject=args.get("subject"),
        text=args.get("text"),
        html=args.get("html"),
        attachments=args.get("attachments"),
        folder=args.get("folder"),
        flags=args.get("flags"),
        labels=args.get("labels"),
    )
    return json.dumps(result, indent=2)


async def handle_message_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle message_get tool."""
    result = await client.get_message(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        message_id=args["message_id"],
        eml=args.get("eml"),
        nodemailer=args.get("nodemailer"),
        attachments=args.get("attachments"),
        raw=args.get("raw"),
    )
    return json.dumps(result, indent=2)


async def handle_message_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle message_update tool."""
    result = await client.update_message(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        message_id=args["message_id"],
        flags=args.get("flags"),
        labels=args.get("labels"),
        folder=args.get("folder"),
    )
    return json.dumps(result, indent=2)


async def handle_message_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle message_delete tool."""
    result = await client.delete_message(
        alias_username=args["alias_username"],
        alias_password=args["alias_password"],
        message_id=args["message_id"],
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "messages_list": handle_messages_list,
    "message_create": handle_message_create,
    "message_get": handle_message_get,
    "message_update": handle_message_update,
    "message_delete": handle_message_delete,
}
