"""Endpoint-level tests for ForwardEmail MCP client and tool handlers.

These use respx to mock the ForwardEmail API and assert the most important
behaviors introduced by the upstream sync:
  * the invite_accept breaking-change fix (now token-scoped),
  * per-request alias-credential (Basic) auth vs. the default API key,
  * the content-type fix (JSON bodies vs. form bodies),
  * the full tool/handler wiring.
"""

import base64
import json

import httpx
import respx

from forwardemail_mcp.client import ForwardEmailClient
from forwardemail_mcp.server import ALL_TOOLS, TOOL_HANDLERS
from forwardemail_mcp.tools import contacts, domains, folders

BASE = "https://api.forwardemail.net"


def _basic_auth(request: httpx.Request) -> str:
    """Decode a request's Basic Authorization header to 'user:pass'."""
    header = request.headers["authorization"]
    scheme, _, token = header.partition(" ")
    assert scheme.lower() == "basic"
    return base64.b64decode(token).decode()


# ---------------------------------------------------------------------------
# Wiring guard
# ---------------------------------------------------------------------------

def test_all_tools_have_handlers():
    """Every tool maps to exactly one handler and there are no name clashes."""
    names = [t.name for t in ALL_TOOLS]
    assert len(names) == len(set(names)), "duplicate tool names"
    assert set(names) == set(TOOL_HANDLERS)
    assert len(ALL_TOOLS) == 71


# ---------------------------------------------------------------------------
# Invite breaking-change fix
# ---------------------------------------------------------------------------

@respx.mock
async def test_invite_accept_uses_token_path(mock_api_key):
    """accept_invite must hit /invites/{token}, not the old /invites path."""
    route = respx.get(f"{BASE}/v1/domains/example.com/invites/TOKEN123").mock(
        return_value=httpx.Response(200, json={"message": "Invite accepted"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        result = await client.accept_invite("example.com", "TOKEN123")

    assert route.called
    assert result["message"] == "Invite accepted"


# ---------------------------------------------------------------------------
# Auth: default API key vs. per-request alias credentials
# ---------------------------------------------------------------------------

@respx.mock
async def test_default_requests_use_api_key(mock_api_key):
    """Account-level calls authenticate with the API key as the username."""
    route = respx.get(f"{BASE}/v1/account").mock(
        return_value=httpx.Response(200, json={"email": "me@example.com"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        await client.get_account()

    assert _basic_auth(route.calls.last.request) == "test_api_key_12345:"


@respx.mock
async def test_alias_requests_use_alias_credentials(mock_api_key, alias_creds):
    """Alias-auth calls override the client default with alias credentials."""
    route = respx.get(f"{BASE}/v1/contacts").mock(
        return_value=httpx.Response(200, json=[])
    )
    async with ForwardEmailClient(mock_api_key) as client:
        await client.list_contacts(*alias_creds)

    assert _basic_auth(route.calls.last.request) == "alias@example.com:secretpass"


# ---------------------------------------------------------------------------
# Content-type: JSON bodies vs. form bodies
# ---------------------------------------------------------------------------

@respx.mock
async def test_json_body_sets_json_content_type(mock_api_key, alias_creds):
    """JSON endpoints send application/json (not the old global form header)."""
    route = respx.post(f"{BASE}/v1/folders").mock(
        return_value=httpx.Response(201, json={"path": "INBOX/Test"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        await client.create_folder(*alias_creds, path="INBOX/Test")

    request = route.calls.last.request
    assert request.headers["content-type"] == "application/json"
    assert json.loads(request.content) == {"path": "INBOX/Test"}


@respx.mock
async def test_form_body_still_uses_form_content_type(mock_api_key):
    """Existing form endpoints keep application/x-www-form-urlencoded."""
    route = respx.post(f"{BASE}/v1/encrypt").mock(
        return_value=httpx.Response(200, json={"encrypted": "abc"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        await client.encrypt_txt_record("forward-email=me@example.com")

    request = route.calls.last.request
    assert request.headers["content-type"] == "application/x-www-form-urlencoded"
    assert b"input=" in request.content


# ---------------------------------------------------------------------------
# Handler-level smoke tests for new tools
# ---------------------------------------------------------------------------

@respx.mock
async def test_allowlist_update_handler(mock_api_key):
    """domain_allowlist_update PUTs a JSON {"allowlist": [...]} body."""
    route = respx.put(f"{BASE}/v1/domains/example.com/allowlist").mock(
        return_value=httpx.Response(200, json={"name": "example.com"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        out = await domains.HANDLERS["domain_allowlist_update"](
            client, {"domain": "example.com", "allowlist": ["1.2.3.4", "*.com"]}
        )

    assert route.called
    assert json.loads(route.calls.last.request.content) == {
        "allowlist": ["1.2.3.4", "*.com"]
    }
    assert "example.com" in out


@respx.mock
async def test_allowlist_update_can_clear(mock_api_key):
    """An empty list is preserved (clears the allowlist), not dropped as None."""
    route = respx.put(f"{BASE}/v1/domains/example.com/allowlist").mock(
        return_value=httpx.Response(200, json={"name": "example.com"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        await domains.HANDLERS["domain_allowlist_update"](
            client, {"domain": "example.com", "allowlist": []}
        )

    assert json.loads(route.calls.last.request.content) == {"allowlist": []}


@respx.mock
async def test_contact_create_handler(mock_api_key, alias_creds):
    """contact_create sends alias auth + a JSON body with array fields intact."""
    route = respx.post(f"{BASE}/v1/contacts").mock(
        return_value=httpx.Response(201, json={"id": "c1", "object": "contact"})
    )
    async with ForwardEmailClient(mock_api_key) as client:
        out = await contacts.HANDLERS["contact_create"](
            client,
            {
                "alias_username": alias_creds[0],
                "alias_password": alias_creds[1],
                "full_name": "Ada Lovelace",
                "emails": [{"value": "ada@example.com", "type": "INTERNET"}],
            },
        )

    request = route.calls.last.request
    assert _basic_auth(request) == "alias@example.com:secretpass"
    body = json.loads(request.content)
    assert body["full_name"] == "Ada Lovelace"
    assert body["emails"][0]["value"] == "ada@example.com"
    assert "c1" in out
