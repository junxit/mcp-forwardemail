# MCP Python SDK 2.x migration

**Status:** not started — deferred deliberately. The dependency is pinned to
`mcp>=1.28,<2` in `pyproject.toml`, so nothing is broken today.

## Why this exists

MCP Python SDK **2.0.0** shipped on 2026-07-28. Two facts make it a hazard for
this project rather than a routine upgrade:

1. `pip install mcp` (and therefore a fresh `uvx --from git+...` resolve) now
   installs 2.x by default.
2. SDK 2.0 rebuilt the low-level `Server` — the exact API `src/forwardemail_mcp/server.py`
   is written against.

Before v0.3.0 the dependency was declared as `mcp>=1.0.0` with no ceiling, so a
new user installing from GitHub would resolve 2.0.0 and get a server that fails
to start. Local development was unaffected only because `uv.lock` pinned 1.26.0.
v0.3.0 added the `<2` ceiling to close that gap.

SDK 1.x is in maintenance mode and receives security fixes only, so this
migration should happen eventually — just not on four days' notice.

## What changes in v2

Scope is small: **`server.py` is the only source file affected.** The client,
all fifteen tool modules, and every tool schema are SDK-version agnostic.

| v1 (current) | v2 |
|---|---|
| `@server.list_tools()` decorator | `Server(on_list_tools=...)` constructor param |
| `@server.call_tool()` decorator | `Server(on_call_tool=...)` constructor param |
| Positional constructor args | Constructor args are **keyword-only** |
| Return values auto-wrapped | Automatic wrapping removed — return explicit protocol types |
| Handler exceptions → `CallToolResult(is_error=True)` | No auto-conversion; construct the error result yourself |

Imports themselves largely survive — `mcp.server.Server`, `mcp.server.stdio.stdio_server`,
`mcp.types.Tool`, and `mcp.types.TextContent` all still exist in v2.

### Impact on our error handling

`server.py`'s `call_tool` wraps every handler in a `try/except` that scrubs 401
responses so an invalid API key can't leak into tool output:

```python
except Exception as e:
    error_msg = str(e)
    if "401" in error_msg or "Unauthorized" in error_msg:
        error_msg = "Authentication failed. Please check your FORWARDEMAIL_API_KEY."
    return [TextContent(type="text", text=f"Error: {error_msg}")]
```

This must keep working. Under v2 the surrounding contract changes (no automatic
exception conversion, no automatic return wrapping), so verify the scrubbing
branch still runs and still returns a well-formed error result — don't assume the
`try/except` carries over untouched.

## Plan when we do it

1. Read the official migration guide and the v2 API reference for the low-level
   server; confirm the exact `run()` signature and whether
   `create_initialization_options()` survives (the migration guide doesn't say).
2. Rewrite `server.py`: move the two decorated handlers to module-level functions
   passed as `on_list_tools=` / `on_call_tool=`; make the `Server(...)` call
   keyword-only; wrap return values explicitly.
3. Re-verify the 401-scrubbing branch above.
4. Change the pin to `mcp>=2,<3` and run `uv lock`.
5. Run the suite (`uv run --extra dev pytest`) — the wiring-guard test asserting
   71 tools with matching handlers is the main regression net.
6. Smoke-test over real stdio JSON-RPC (`initialize` → `tools/list`) and confirm
   71 tools come back; unit tests alone won't catch a protocol-level break.
7. Update the README prerequisites note and `pyproject.toml` comment.

## References

- Migration guide: <https://py.sdk.modelcontextprotocol.io/migration/>
- What's new in v2: <https://py.sdk.modelcontextprotocol.io/whats-new/>
- v2.0.0 release notes: <https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.0.0>
- v1.x maintenance branch: <https://github.com/modelcontextprotocol/python-sdk/tree/v1.x>
