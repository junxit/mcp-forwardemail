"""Alias management tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="aliases_list",
        description="List all aliases for a domain. Supports pagination and search.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "query": {
                    "type": "string",
                    "description": "Search query to filter aliases by name or recipient",
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
            "required": ["domain"],
        },
    ),
    Tool(
        name="alias_create",
        description="Create a new email alias for a domain.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "name": {
                    "type": "string",
                    "description": "Alias name (the part before @domain)",
                },
                "recipients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of recipient email addresses to forward to",
                },
                "description": {
                    "type": "string",
                    "description": "Description of this alias",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels for organizing aliases",
                },
                "is_enabled": {
                    "type": "boolean",
                    "description": "Whether the alias is enabled",
                    "default": True,
                },
                "has_imap": {
                    "type": "boolean",
                    "description": "Enable IMAP storage for this alias",
                },
                "has_pgp": {
                    "type": "boolean",
                    "description": "Enable PGP encryption",
                },
                "public_key": {
                    "type": "string",
                    "description": "PGP public key for encryption",
                },
                "has_recipient_verification": {
                    "type": "boolean",
                    "description": "Require recipients to confirm before forwarding",
                },
                "max_quota": {
                    "type": "string",
                    "description": "Maximum storage quota for this alias (e.g. '1 GB')",
                },
                "has_wkd_disabled": {
                    "type": "boolean",
                    "description": "Disable WKD (Web Key Directory) public key lookup for this alias",
                },
                "smtp_limit": {
                    "type": "integer",
                    "minimum": 0,
                    "description": (
                        "Per-alias daily SMTP outbound limit; 0 uses the domain limit. "
                        "Requires domain-admin permission - omit unless explicitly setting it. "
                        "Capped by the domain's effective limit"
                    ),
                },
            },
            "required": ["domain", "name"],
        },
    ),
    Tool(
        name="alias_get",
        description="Get details of a specific alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
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
        name="alias_update",
        description="Update an existing alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "name": {
                    "type": "string",
                    "description": "New alias name",
                },
                "recipients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New list of recipient email addresses",
                },
                "description": {
                    "type": "string",
                    "description": "New description",
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New labels",
                },
                "is_enabled": {
                    "type": "boolean",
                    "description": "Whether the alias is enabled",
                },
                "has_imap": {
                    "type": "boolean",
                    "description": "Enable IMAP storage",
                },
                "has_pgp": {
                    "type": "boolean",
                    "description": "Enable PGP encryption",
                },
                "public_key": {
                    "type": "string",
                    "description": "PGP public key",
                },
                "has_recipient_verification": {
                    "type": "boolean",
                    "description": "Require recipients to confirm before forwarding",
                },
                "max_quota": {
                    "type": "string",
                    "description": "Maximum storage quota for this alias (e.g. '1 GB')",
                },
                "has_wkd_disabled": {
                    "type": "boolean",
                    "description": "Disable WKD (Web Key Directory) public key lookup for this alias",
                },
                "smtp_limit": {
                    "type": "integer",
                    "minimum": 0,
                    "description": (
                        "Per-alias daily SMTP outbound limit; 0 uses the domain limit. "
                        "Requires domain-admin permission - omit unless explicitly setting it. "
                        "Does not reset the daily count or clear an existing suspension"
                    ),
                },
            },
            "required": ["domain", "alias_id"],
        },
    ),
    Tool(
        name="alias_delete",
        description="Delete an alias.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name to delete",
                },
            },
            "required": ["domain", "alias_id"],
        },
    ),
    Tool(
        name="alias_generate_password",
        description="Generate a password for an alias to use with IMAP/SMTP/CalDAV/CardDAV.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "alias_id": {
                    "type": "string",
                    "description": "Alias ID or name",
                },
                "new_password": {
                    "type": "string",
                    "description": "Specific password to use (optional, auto-generated if not provided)",
                },
                "is_override": {
                    "type": "boolean",
                    "description": "Override existing password if one exists",
                },
                "emailed_instructions": {
                    "type": "boolean",
                    "description": "Email setup instructions to the alias",
                },
            },
            "required": ["domain", "alias_id"],
        },
    ),
]


async def handle_aliases_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle aliases_list tool."""
    result, pagination = await client.list_aliases(
        domain=args["domain"],
        query=args.get("query"),
        sort=args.get("sort"),
        page=args.get("page"),
        limit=args.get("limit"),
    )
    response = {"aliases": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_alias_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle alias_create tool."""
    result = await client.create_alias(
        domain=args["domain"],
        name=args["name"],
        recipients=args.get("recipients"),
        description=args.get("description"),
        labels=args.get("labels"),
        has_recipient_verification=args.get("has_recipient_verification"),
        is_enabled=args.get("is_enabled"),
        has_imap=args.get("has_imap"),
        has_pgp=args.get("has_pgp"),
        public_key=args.get("public_key"),
        max_quota=args.get("max_quota"),
        has_wkd_disabled=args.get("has_wkd_disabled"),
        smtp_limit=args.get("smtp_limit"),
    )
    return json.dumps(result, indent=2)


async def handle_alias_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle alias_get tool."""
    result = await client.get_alias(
        domain=args["domain"],
        alias_id=args["alias_id"],
    )
    return json.dumps(result, indent=2)


async def handle_alias_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle alias_update tool."""
    result = await client.update_alias(
        domain=args["domain"],
        alias_id=args["alias_id"],
        name=args.get("name"),
        recipients=args.get("recipients"),
        description=args.get("description"),
        labels=args.get("labels"),
        has_recipient_verification=args.get("has_recipient_verification"),
        is_enabled=args.get("is_enabled"),
        has_imap=args.get("has_imap"),
        has_pgp=args.get("has_pgp"),
        public_key=args.get("public_key"),
        max_quota=args.get("max_quota"),
        has_wkd_disabled=args.get("has_wkd_disabled"),
        smtp_limit=args.get("smtp_limit"),
    )
    return json.dumps(result, indent=2)


async def handle_alias_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle alias_delete tool."""
    result = await client.delete_alias(
        domain=args["domain"],
        alias_id=args["alias_id"],
    )
    return json.dumps(result, indent=2)


async def handle_alias_generate_password(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle alias_generate_password tool."""
    result = await client.generate_alias_password(
        domain=args["domain"],
        alias_id=args["alias_id"],
        new_password=args.get("new_password"),
        is_override=args.get("is_override"),
        emailed_instructions=args.get("emailed_instructions"),
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "aliases_list": handle_aliases_list,
    "alias_create": handle_alias_create,
    "alias_get": handle_alias_get,
    "alias_update": handle_alias_update,
    "alias_delete": handle_alias_delete,
    "alias_generate_password": handle_alias_generate_password,
}
