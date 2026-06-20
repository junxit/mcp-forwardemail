"""Domain management tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="domains_list",
        description="List all domains in your ForwardEmail account. Supports pagination and search.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to filter domains by name",
                },
                "sort": {
                    "type": "string",
                    "description": "Sort field (prefix with - for descending, e.g., '-created_at')",
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
        name="domain_create",
        description="Create a new domain in your ForwardEmail account.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name to add (e.g., 'example.com')",
                },
                "plan": {
                    "type": "string",
                    "description": "Plan type: 'free', 'enhanced_protection', or 'team'",
                    "enum": ["free", "enhanced_protection", "team"],
                    "default": "free",
                },
                "catchall": {
                    "type": "boolean",
                    "description": "Enable catch-all for unmatched addresses",
                },
                "has_adult_content_protection": {
                    "type": "boolean",
                    "description": "Enable adult content filtering",
                },
                "has_phishing_protection": {
                    "type": "boolean",
                    "description": "Enable phishing protection",
                },
                "has_executable_protection": {
                    "type": "boolean",
                    "description": "Enable executable attachment blocking",
                },
                "has_virus_protection": {
                    "type": "boolean",
                    "description": "Enable virus scanning",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_get",
        description="Get details of a specific domain.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_update",
        description="Update domain settings.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "smtp_port": {
                    "type": "string",
                    "description": "SMTP port (default: '25')",
                },
                "has_adult_content_protection": {
                    "type": "boolean",
                    "description": "Enable adult content filtering",
                },
                "has_phishing_protection": {
                    "type": "boolean",
                    "description": "Enable phishing protection",
                },
                "has_executable_protection": {
                    "type": "boolean",
                    "description": "Enable executable attachment blocking",
                },
                "has_virus_protection": {
                    "type": "boolean",
                    "description": "Enable virus scanning",
                },
                "has_recipient_verification": {
                    "type": "boolean",
                    "description": "Enable recipient verification",
                },
                "retention_days": {
                    "type": "integer",
                    "description": "Log retention days (0-30)",
                },
                "bounce_webhook": {
                    "type": "string",
                    "description": "Webhook URL for bounce notifications",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_delete",
        description="Delete a domain from your account.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID to delete",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_verify_records",
        description="Verify DNS records (MX, TXT) for a domain.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name to verify",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_verify_smtp",
        description="Verify SMTP records (DKIM, Return-Path, DMARC) for outbound email.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name to verify",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_catchall_passwords_list",
        description="List domain-wide catch-all passwords.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_catchall_password_create",
        description="Create a domain-wide catch-all password for IMAP/SMTP access.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "new_password": {
                    "type": "string",
                    "description": "Specific password to use (optional, auto-generated if not provided)",
                },
                "description": {
                    "type": "string",
                    "description": "Description for this password",
                },
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="domain_catchall_password_delete",
        description="Delete a domain-wide catch-all password.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name",
                },
                "token_id": {
                    "type": "string",
                    "description": "Password token ID to delete",
                },
            },
            "required": ["domain", "token_id"],
        },
    ),
    Tool(
        name="domain_allowlist_update",
        description="Replace a domain's sender allowlist. Pass an empty list to clear it.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "allowlist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Allowlisted senders: IP addresses, FQDNs, email addresses, "
                        "or wildcard TLDs such as '*.com'. Empty list clears the allowlist."
                    ),
                },
            },
            "required": ["domain", "allowlist"],
        },
    ),
    Tool(
        name="domain_denylist_update",
        description="Replace a domain's sender denylist. Pass an empty list to clear it.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
                "denylist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Denylisted senders: IP addresses, FQDNs, email addresses, "
                        "or wildcard TLDs such as '*.com'. Empty list clears the denylist."
                    ),
                },
            },
            "required": ["domain", "denylist"],
        },
    ),
    Tool(
        name="domain_test_s3_connection",
        description="Test the domain's custom S3 storage connection (credentials and bucket access).",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name or ID",
                },
            },
            "required": ["domain"],
        },
    ),
]


async def handle_domains_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domains_list tool."""
    result, pagination = await client.list_domains(
        query=args.get("query"),
        sort=args.get("sort"),
        page=args.get("page"),
        limit=args.get("limit"),
    )
    response = {"domains": result}
    if pagination:
        response["pagination"] = pagination.model_dump()
    return json.dumps(response, indent=2)


async def handle_domain_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_create tool."""
    result = await client.create_domain(
        domain=args["domain"],
        plan=args.get("plan", "free"),
        catchall=args.get("catchall"),
        has_adult_content_protection=args.get("has_adult_content_protection"),
        has_phishing_protection=args.get("has_phishing_protection"),
        has_executable_protection=args.get("has_executable_protection"),
        has_virus_protection=args.get("has_virus_protection"),
    )
    return json.dumps(result, indent=2)


async def handle_domain_get(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_get tool."""
    result = await client.get_domain(args["domain"])
    return json.dumps(result, indent=2)


async def handle_domain_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_update tool."""
    result = await client.update_domain(
        domain=args["domain"],
        smtp_port=args.get("smtp_port"),
        has_adult_content_protection=args.get("has_adult_content_protection"),
        has_phishing_protection=args.get("has_phishing_protection"),
        has_executable_protection=args.get("has_executable_protection"),
        has_virus_protection=args.get("has_virus_protection"),
        has_recipient_verification=args.get("has_recipient_verification"),
        retention_days=args.get("retention_days"),
        bounce_webhook=args.get("bounce_webhook"),
    )
    return json.dumps(result, indent=2)


async def handle_domain_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_delete tool."""
    result = await client.delete_domain(args["domain"])
    return json.dumps(result, indent=2)


async def handle_domain_verify_records(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_verify_records tool."""
    result = await client.verify_domain_records(args["domain"])
    return json.dumps(result, indent=2)


async def handle_domain_verify_smtp(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_verify_smtp tool."""
    result = await client.verify_domain_smtp(args["domain"])
    return json.dumps(result, indent=2)


async def handle_domain_catchall_passwords_list(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_catchall_passwords_list tool."""
    result = await client.list_catchall_passwords(args["domain"])
    return json.dumps({"passwords": result}, indent=2)


async def handle_domain_catchall_password_create(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_catchall_password_create tool."""
    result = await client.create_catchall_password(
        domain=args["domain"],
        new_password=args.get("new_password"),
        description=args.get("description"),
    )
    return json.dumps(result, indent=2)


async def handle_domain_catchall_password_delete(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_catchall_password_delete tool."""
    result = await client.delete_catchall_password(
        domain=args["domain"],
        token_id=args["token_id"],
    )
    return json.dumps(result, indent=2)


async def handle_domain_allowlist_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_allowlist_update tool."""
    result = await client.update_allowlist(
        domain=args["domain"],
        allowlist=args["allowlist"],
    )
    return json.dumps(result, indent=2)


async def handle_domain_denylist_update(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_denylist_update tool."""
    result = await client.update_denylist(
        domain=args["domain"],
        denylist=args["denylist"],
    )
    return json.dumps(result, indent=2)


async def handle_domain_test_s3_connection(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle domain_test_s3_connection tool."""
    result = await client.test_s3_connection(args["domain"])
    return json.dumps(result, indent=2)


HANDLERS = {
    "domains_list": handle_domains_list,
    "domain_create": handle_domain_create,
    "domain_get": handle_domain_get,
    "domain_update": handle_domain_update,
    "domain_delete": handle_domain_delete,
    "domain_verify_records": handle_domain_verify_records,
    "domain_verify_smtp": handle_domain_verify_smtp,
    "domain_catchall_passwords_list": handle_domain_catchall_passwords_list,
    "domain_catchall_password_create": handle_domain_catchall_password_create,
    "domain_catchall_password_delete": handle_domain_catchall_password_delete,
    "domain_allowlist_update": handle_domain_allowlist_update,
    "domain_denylist_update": handle_domain_denylist_update,
    "domain_test_s3_connection": handle_domain_test_s3_connection,
}
