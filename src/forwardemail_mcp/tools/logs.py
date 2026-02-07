"""Log management tools for ForwardEmail MCP."""

import json
from typing import Any
from mcp.types import Tool

from ..client import ForwardEmailClient


TOOLS = [
    Tool(
        name="logs_download",
        description="Request a log download. Logs will be emailed to you as a gzip-compressed CSV attachment. Limited to 10 requests per day.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Filter logs by domain (optional)",
                },
                "query": {
                    "type": "string",
                    "description": "Search query or date filter (e.g., 'M/D/YY' format)",
                },
            },
            "required": [],
        },
    ),
]


async def handle_logs_download(client: ForwardEmailClient, args: dict[str, Any]) -> str:
    """Handle logs_download tool."""
    result = await client.download_logs(
        domain=args.get("domain"),
        query=args.get("query"),
    )
    return json.dumps(result, indent=2)


HANDLERS = {
    "logs_download": handle_logs_download,
}
