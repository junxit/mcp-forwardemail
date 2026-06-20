# ForwardEmail MCP Server

> ⚠️ **UNOFFICIAL** - This is an unofficial MCP server for [ForwardEmail](https://forwardemail.net). It is not affiliated with, endorsed by, or supported by Forward Email LLC.

An MCP (Model Context Protocol) server that provides comprehensive access to the ForwardEmail API for Claude Desktop, Cline, and other MCP-compatible clients.

## Features

- **71 MCP tools** covering the ForwardEmail API
- **Domain Management** - List, create, update, delete domains; verify DNS/SMTP records; allowlist/denylist; S3 connection test
- **Alias Management** - Full CRUD for email aliases with forwarding rules
- **Outbound Email** - Send emails via API, check limits, manage queue
- **Sieve Filtering** - Manage server-side Sieve filtering scripts
- **Mailbox (alias credentials)** - Contacts (CardDAV), Calendars & events (CalDAV), Messages & Folders (IMAP)
- **Team Collaboration** - Invite members, manage roles
- **Security** - Password generation for IMAP/SMTP access, TXT record encryption
- **Async/Await** - Built with modern Python async patterns
- **Type Safety** - Full type hints with Pydantic models

## Prerequisites

- **Python**: 3.10+
- **uv**: 0.4+ (recommended)
- **uvx**: Included with uv
- A ForwardEmail account with API access
- API key from [ForwardEmail Security Settings](https://forwardemail.net/my-account/security)

## Installation

### Using uvx (Recommended)

```bash
uvx --from git+https://github.com/junxit/mcp-forwardemail.git forwardemail-mcp
```

### Using pip

```bash
pip install git+https://github.com/junxit/mcp-forwardemail.git
```

### From Source

```bash
git clone https://github.com/junxit/mcp-forwardemail.git
cd mcp-forwardemail
uv pip install -e .
```

## Configuration

### Claude Desktop

Add to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "forwardemail": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/junxit/mcp-forwardemail.git", "forwardemail-mcp"],
      "env": {
        "FORWARDEMAIL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Local Development with Claude Desktop

```json
{
  "mcpServers": {
    "forwardemail": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-forwardemail", "run", "forwardemail-mcp"],
      "env": {
        "FORWARDEMAIL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Cline / Continue Extension

Add to your MCP settings:

```json
{
  "forwardemail": {
    "command": "uvx",
    "args": ["--from", "git+https://github.com/junxit/mcp-forwardemail.git", "forwardemail-mcp"],
    "env": {
      "FORWARDEMAIL_API_KEY": "your_api_key_here"
    }
  }
}
```

### Environment Variable

Alternatively, set the API key as an environment variable:

```bash
export FORWARDEMAIL_API_KEY="your_api_key_here"
```

### Alias Credentials (for mailbox tools)

Most tools authenticate with your account API key. The mailbox tools — **Contacts**,
**Calendars**, **Calendar Events**, **Messages**, **Folders**, and **Sieve Scripts**
(the alias-auth variant) — instead use a specific alias's own credentials, so each of
those tools takes two extra arguments:

- `alias_username` — the full alias email (e.g. `me@example.com`)
- `alias_password` — a password generated for that alias via `alias_generate_password`

These are passed per tool call (no extra environment variables), so you can work with
any alias across any domain in the same session. Generate a password first:

> *"Generate an IMAP/CardDAV password for the alias `me@example.com`, then list its folders."*

## Available Tools

### Account (3 tools)
| Tool | Description |
|------|-------------|
| `account_get` | Retrieve account information |
| `account_create` | Create a new account |
| `account_update` | Update account details |

### Domains (13 tools)
| Tool | Description |
|------|-------------|
| `domains_list` | List all domains |
| `domain_create` | Create a new domain |
| `domain_get` | Get domain details |
| `domain_update` | Update domain settings |
| `domain_delete` | Delete a domain |
| `domain_verify_records` | Verify DNS records |
| `domain_verify_smtp` | Verify SMTP records (DKIM, DMARC) |
| `domain_catchall_passwords_list` | List catch-all passwords |
| `domain_catchall_password_create` | Create catch-all password |
| `domain_catchall_password_delete` | Delete catch-all password |
| `domain_allowlist_update` | Replace the domain sender allowlist |
| `domain_denylist_update` | Replace the domain sender denylist |
| `domain_test_s3_connection` | Test custom S3 storage connection |

### Aliases (6 tools)
| Tool | Description |
|------|-------------|
| `aliases_list` | List domain aliases |
| `alias_create` | Create a new alias |
| `alias_get` | Get alias details |
| `alias_update` | Update an alias |
| `alias_delete` | Delete an alias |
| `alias_generate_password` | Generate IMAP/SMTP password |

### Outbound Emails (5 tools)
| Tool | Description |
|------|-------------|
| `emails_limit_get` | Get daily sending limit |
| `emails_list` | List outbound emails |
| `email_create` | Send an email |
| `email_get` | Get email details |
| `email_delete` | Cancel/delete an email |

### Invites (3 tools)
| Tool | Description |
|------|-------------|
| `invite_accept` | Accept a domain invite (requires the invite `token`) |
| `invite_create` | Invite a user to domain |
| `invite_delete` | Remove an invite |

### Members (2 tools)
| Tool | Description |
|------|-------------|
| `member_update` | Update member role |
| `member_delete` | Remove a member |

### Logs (1 tool)
| Tool | Description |
|------|-------------|
| `logs_download` | Request log download (emailed as CSV) |

### Encrypt (1 tool)
| Tool | Description |
|------|-------------|
| `encrypt_txt_record` | Encrypt TXT record value |

### Sieve Filters — domain (6 tools, API key)
| Tool | Description |
|------|-------------|
| `domain_sieve_list` | List an alias's Sieve scripts |
| `domain_sieve_create` | Create a Sieve script |
| `domain_sieve_get` | Get a Sieve script |
| `domain_sieve_update` | Update a Sieve script |
| `domain_sieve_delete` | Delete a Sieve script |
| `domain_sieve_activate` | Activate a Sieve script |

The tool groups below use **alias credentials** (`alias_username` + `alias_password`) — see [Alias Credentials](#alias-credentials-for-mailbox-tools).

### Contacts — CardDAV (5 tools)
| Tool | Description |
|------|-------------|
| `contacts_list` | List contacts |
| `contact_create` | Create a contact |
| `contact_get` | Get a contact |
| `contact_update` | Update a contact |
| `contact_delete` | Delete a contact |

### Calendars — CalDAV (5 tools)
| Tool | Description |
|------|-------------|
| `calendars_list` | List calendars |
| `calendar_create` | Create a calendar |
| `calendar_get` | Get a calendar |
| `calendar_update` | Update a calendar |
| `calendar_delete` | Delete a calendar |

### Calendar Events — CalDAV (5 tools)
| Tool | Description |
|------|-------------|
| `calendar_events_list` | List calendar events |
| `calendar_event_create` | Create an event (iCalendar) |
| `calendar_event_get` | Get an event |
| `calendar_event_update` | Update an event |
| `calendar_event_delete` | Delete an event |

### Messages — IMAP (5 tools)
| Tool | Description |
|------|-------------|
| `messages_list` | List and search messages |
| `message_create` | Create/append a message |
| `message_get` | Get a message |
| `message_update` | Update flags/labels/folder |
| `message_delete` | Delete a message |

### Folders — IMAP (5 tools)
| Tool | Description |
|------|-------------|
| `folders_list` | List folders |
| `folder_create` | Create a folder |
| `folder_get` | Get a folder |
| `folder_update` | Rename a folder |
| `folder_delete` | Delete a folder |

### Sieve Scripts — alias auth (6 tools)
| Tool | Description |
|------|-------------|
| `sieve_scripts_list` | List Sieve scripts |
| `sieve_script_create` | Create a Sieve script |
| `sieve_script_get` | Get a Sieve script |
| `sieve_script_update` | Update a Sieve script |
| `sieve_script_delete` | Delete a Sieve script |
| `sieve_script_activate` | Activate a Sieve script |

## Usage Examples

### List Your Domains

Ask Claude: *"List my ForwardEmail domains"*

### Create an Email Alias

Ask Claude: *"Create an alias called 'support' on example.com that forwards to admin@gmail.com"*

### Send an Email

Ask Claude: *"Send an email from hello@example.com to user@gmail.com with subject 'Test' and body 'Hello!'"*

### Verify Domain Setup

Ask Claude: *"Verify the DNS records for example.com"*

## API Coverage Notes

The ForwardEmail Contacts (CardDAV), Calendars/Events (CalDAV), Messages and Folders
(IMAP), and alias Sieve scripts authenticate with **alias credentials** (alias email +
generated password) rather than the account API key. These are now **fully supported** —
see [Alias Credentials](#alias-credentials-for-mailbox-tools) for how to supply them.

Not currently wrapped:

- **Push tokens** (`/v1/push-tokens`) — registering a device push token requires a real
  device/browser to mint the token value, so it is out of scope for this server.
- Internal/billing endpoints (Stripe, PayPal, WebSocket, etc.).

## Troubleshooting

### "Authentication failed" error

- Verify your API key is correct
- Check that the key is properly set in `env` section of your MCP config
- Ensure there are no extra spaces or quotes around the key

### "FORWARDEMAIL_API_KEY environment variable is required"

- Make sure you've added the `env` section to your MCP configuration
- Restart Claude Desktop after changing the configuration

### Tool not found

- Restart Claude Desktop to reload MCP servers
- Check Claude Desktop logs for startup errors

## Development

```bash
# Clone the repository
git clone https://github.com/junxit/mcp-forwardemail.git
cd mcp-forwardemail

# Install in development mode
uv pip install -e ".[dev]"

# Run tests (--extra dev pulls pytest/respx)
uv run --extra dev pytest -v

# Run the server locally
FORWARDEMAIL_API_KEY="your_key" uv run forwardemail-mcp
```

## How to Test

```bash
# Run unit tests
uv run --extra dev pytest -v

# Run single test file
uv run --extra dev pytest tests/test_endpoints.py -v
```

## How to Uninstall

```bash
# If installed via pip/uv
pip uninstall forwardemail-mcp

# Remove from Claude Desktop config
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json
# and remove the "forwardemail" entry from mcpServers
```

### Cleanup Local Files

```bash
# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove virtual environments
rm -rf .venv venv ENV .uv

# Remove build artifacts
rm -rf build dist *.egg-info .eggs

# Remove test/coverage artifacts
rm -rf .pytest_cache .coverage htmlcov .tox

# Remove the project directory (if installed from source)
cd .. && rm -rf mcp-forwardemail
```

## Assumptions

- ForwardEmail API remains stable at `https://api.forwardemail.net`
- API authentication continues to use HTTP Basic Auth
- MCP SDK version 1.0+ maintains current interface
- Users have valid ForwardEmail accounts with API access enabled

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Links

- [ForwardEmail](https://forwardemail.net) - The email service
- [ForwardEmail API Docs](https://forwardemail.net/en/email-api) - Official API documentation
- [ForwardEmail GitHub](https://github.com/forwardemail) - Official GitHub organization
- [MCP Documentation](https://modelcontextprotocol.io) - Model Context Protocol docs

## License

MIT License - see [LICENSE](LICENSE) file.

---

**Disclaimer**: This is an unofficial, community-maintained project. ForwardEmail is a trademark of Forward Email LLC. This project is not affiliated with, endorsed by, or supported by Forward Email LLC.
