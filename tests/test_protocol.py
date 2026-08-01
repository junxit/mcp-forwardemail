"""Protocol-level tests driving the MCP server in-process.

These use the SDK's in-memory client transport, so they exercise the real
request/response path — handler dispatch, result wrapping, and error flagging —
rather than calling handler functions directly. That is the layer the SDK v2
migration changed, and the layer unit tests cannot reach.
"""

import json

import httpx
import respx
from mcp import Client

from forwardemail_mcp.client import ForwardEmailClient
from forwardemail_mcp.server import create_server

BASE = "https://api.forwardemail.net"


async def test_protocol_list_tools(mock_api_key):
    """tools/list returns every registered tool over the wire."""
    server = create_server(ForwardEmailClient(mock_api_key))
    async with Client(server) as client:
        result = await client.list_tools()

    names = [t.name for t in result.tools]
    assert len(names) == 71
    assert "alias_create" in names
    assert "contacts_list" in names


@respx.mock
async def test_protocol_call_tool_success(mock_api_key):
    """A successful tools/call returns content and is not flagged as an error."""
    respx.get(f"{BASE}/v1/domains").mock(
        return_value=httpx.Response(200, json=[{"name": "example.com"}])
    )

    server = create_server(ForwardEmailClient(mock_api_key))
    async with Client(server) as client:
        result = await client.call_tool("domains_list", {})

    assert not result.is_error
    assert len(result.content) == 1
    payload = json.loads(result.content[0].text)
    assert payload["domains"][0]["name"] == "example.com"


async def test_protocol_call_tool_unknown(mock_api_key):
    """An unknown tool returns an error result rather than raising."""
    server = create_server(ForwardEmailClient(mock_api_key))
    async with Client(server) as client:
        result = await client.call_tool("no_such_tool", {})

    assert result.is_error
    assert "Unknown tool" in result.content[0].text


@respx.mock
async def test_protocol_call_tool_scrubs_auth_error(mock_api_key):
    """A 401 is reported as an error result with the API key message scrubbed."""
    respx.get(f"{BASE}/v1/account").mock(return_value=httpx.Response(401))

    server = create_server(ForwardEmailClient(mock_api_key))
    async with Client(server) as client:
        result = await client.call_tool("account_get", {})

    assert result.is_error
    text = result.content[0].text
    assert "FORWARDEMAIL_API_KEY" in text
    # The raw httpx error (which embeds the request URL) must not leak through.
    assert "401 Unauthorized" not in text
