"""Outbound email tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="emails_limit_get",
        description="Get your daily outbound SMTP email limit and current count.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="emails_list",
        description="List outbound SMTP emails. Does not include message body - use email_get for full details.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "domain": {
                    "type": "string",
                    "description": "Filter by domain",
                },
                "sort": {
                    "type": "string",
                    "description": "Sort field (prefix with - for descending)",
                },
                "page": {
                    "type": "integer",
                    "description": "Page number (1-indexed)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Results per page (10-50)",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="email_create",
        description="Create and send an outbound email via SMTP API.",
        inputSchema={
            "type": "object",
            "properties": {
                "from_addr": {
                    "type": "string",
                    "description": "Sender email address (must be an alias you control)",
                },
                "to": {
                    "type": "string",
                    "description": "Recipient email address(es), comma-separated for multiple",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line",
                },
                "text": {
                    "type": "string",
                    "description": "Plain text body of the email",
                },
                "html": {
                    "type": "string",
                    "description": "HTML body of the email",
                },
                "cc": {
                    "type": "string",
                    "description": "CC recipients, comma-separated",
                },
                "bcc": {
                    "type": "string",
                    "description": "BCC recipients, comma-separated",
                },
                "reply_to": {
                    "type": "string",
                    "description": "Reply-To address",
                },
                "raw": {
                    "type": "string",
                    "description": "Raw email content including headers (alternative to other fields)",
                },
            },
            "required": ["from_addr", "to"],
        },
    ),
    Tool(
        name="email_get",
        description="Get full details of an outbound email including message body and headers.",
        inputSchema={
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "Email ID",
                },
            },
            "required": ["email_id"],
        },
    ),
    Tool(
        name="email_delete",
        description="Delete/cancel an outbound email. Only works for emails with status 'pending', 'queued', or 'deferred'.",
        inputSchema={
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "Email ID to delete",
                },
            },
            "required": ["email_id"],
        },
    ),
]


async def handle_emails_limit_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle emails_limit_get tool."""
    result = await client.get_email_limit()
    return json.dumps(result, indent=2)


async def handle_emails_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle emails_list tool."""
    result, pagination = await client.list_emails(
        query=args.get("query"),
        domain=args.get("domain"),
        sort=args.get("sort"),
        page=args.get("page"),
        limit=args.get("limit"),
    )
    response = {"emails": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_email_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle email_create tool."""
    result = await client.create_email(
        from_addr=args["from_addr"],
        to=args["to"],
        subject=args.get("subject"),
        text=args.get("text"),
        html=args.get("html"),
        cc=args.get("cc"),
        bcc=args.get("bcc"),
        reply_to=args.get("reply_to"),
        raw=args.get("raw"),
    )
    return json.dumps(result, indent=2)


async def handle_email_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle email_get tool."""
    result = await client.get_email(args["email_id"])
    return json.dumps(result, indent=2)


async def handle_email_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle email_delete tool."""
    result = await client.delete_email(args["email_id"])
    return json.dumps(result, indent=2)


HANDLERS = {
    "emails_limit_get": handle_emails_limit_get,
    "emails_list": handle_emails_list,
    "email_create": handle_email_create,
    "email_get": handle_email_get,
    "email_delete": handle_email_delete,
}
