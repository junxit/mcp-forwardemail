# MCP Python SDK 2.x migration

**Status:** completed in v0.4.0 (2026-08-01). The dependency is `mcp>=2,<3`.
If you need SDK 1.x, pin `forwardemail-mcp==0.3.0`.

## Why it was needed

MCP Python SDK **2.0.0** shipped on 2026-07-28 and rebuilt the low-level
`Server` — the API `src/forwardemail_mcp/server.py` is written against. Two facts
made it urgent rather than routine:

1. `pip install mcp` (and a fresh `uvx --from git+...` resolve) installs 2.x.
2. Before v0.3.0 the dependency was declared `mcp>=1.0.0` with no ceiling, so a
   new user would resolve 2.0.0 and get a server that could not start.

v0.3.0 added a `<2` ceiling as a stopgap. v0.4.0 migrated properly. SDK 1.x is in
maintenance mode (security fixes only).

## What actually changed

Scope was small: **`server.py` was the only source file that needed edits.** The
API client and all fifteen tool modules were untouched — `Tool(name=,
description=, inputSchema=)` and `TextContent(type=, text=)` construct
identically in v2, so all 71 tool definitions carried over unchanged.

The imports also survived: `mcp.server.Server`, `mcp.server.stdio.stdio_server`,
`mcp.types.Tool`, and `mcp.types.TextContent` all still exist.

### Handler registration

| v1 | v2 |
|---|---|
| `@server.list_tools()` decorator | `Server(on_list_tools=...)` constructor param |
| `@server.call_tool()` decorator | `Server(on_call_tool=...)` constructor param |
| `Server("name")` | `Server("name", ...)` — everything after `name` is keyword-only |

### Handler signatures

This is the part the official migration guide does not spell out, and where the
real API differs from what a summary of it suggests. Both handlers take
`(ctx, params)` and return a `Result` object — **not** a bare list:

```python
# v1
@server.list_tools()
async def list_tools() -> list[Tool]:
    return ALL_TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    ...
    return [TextContent(type="text", text=str(result))]
```

```python
# v2
async def on_list_tools(
    ctx: ServerRequestContext,
    params: Optional[PaginatedRequestParams],
) -> ListToolsResult:
    return ListToolsResult(tools=ALL_TOOLS)

async def on_call_tool(
    ctx: ServerRequestContext,
    params: CallToolRequestParams,
) -> CallToolResult:
    name = params.name              # was a positional arg
    arguments = params.arguments or {}   # was a positional arg; may be None
    ...
    return CallToolResult(content=[TextContent(type="text", text=str(result))])
```

`CallToolResult.is_error` is the Python field name (wire alias `isError`).

### Error handling

SDK v2 no longer converts a handler exception into `CallToolResult(is_error=True)`.
Every failure path must return a result explicitly — including the unknown-tool
case, which previously did `raise ValueError(...)` and relied on the SDK.

This surfaced a latent bug: in v1 the caught-exception branch returned plain
`TextContent` with no error flag, so clients could not tell a failed call from a
successful one. v0.4.0 returns `is_error=True` for both the unknown-tool and
exception paths. The 401-scrubbing branch that replaces credential-bearing errors
with a generic message is preserved and now has a test.

### Unchanged

`Server.run(read_stream, write_stream, initialization_options, raise_exceptions=False)`
and `server.create_initialization_options()` both survive with the same call
shape, so the `stdio_server()` block needed no edits.

## Testing this layer

`create_server(client)` was extracted from `run_server()` so the configured
server can be driven in-process. `tests/test_protocol.py` uses the SDK's
in-memory client transport (`Client(server)`) to exercise the real
request/response path:

```python
server = create_server(ForwardEmailClient(api_key))
async with Client(server) as client:
    result = await client.call_tool("domains_list", {})
```

This covers `tools/list`, a successful `tools/call`, unknown-tool handling, and
401 scrubbing — the layer the migration changed, and which unit tests calling
handler functions directly cannot reach.

## References

- Migration guide: <https://py.sdk.modelcontextprotocol.io/migration/>
- What's new in v2: <https://py.sdk.modelcontextprotocol.io/whats-new/>
- v2.0.0 release notes: <https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.0.0>
- v1.x maintenance branch: <https://github.com/modelcontextprotocol/python-sdk/tree/v1.x>
