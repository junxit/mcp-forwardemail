"""Encryption tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="encrypt_txt_record",
        description="Encrypt a TXT record value for use in DNS. Useful for encrypting forwarding addresses in DNS records.",
        inputSchema={
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "The value to encrypt (e.g., an email address)",
                },
            },
            "required": ["input"],
        },
    ),
]


async def handle_encrypt_txt_record(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle encrypt_txt_record tool."""
    result = await client.encrypt_txt_record(args["input"])
    return json.dumps(result, indent=2)


HANDLERS = {
    "encrypt_txt_record": handle_encrypt_txt_record,
}
