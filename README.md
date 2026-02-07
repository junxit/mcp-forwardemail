# ForwardEmail MCP Server

> ⚠️ **UNOFFICIAL** - This is an unofficial MCP server for [ForwardEmail](https://forwardemail.net). It is not affiliated with, endorsed by, or supported by Forward Email LLC.

An MCP (Model Context Protocol) server that provides comprehensive access to the ForwardEmail API for Claude Desktop, Cline, and other MCP-compatible clients.

## Features

- **31 MCP tools** covering the ForwardEmail API
- **Domain Management** - List, create, update, delete domains; verify DNS/SMTP records
- **Alias Management** - Full CRUD for email aliases with forwarding rules
- **Outbound Email** - Send emails via API, check limits, manage queue
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
uvx forwardemail-mcp
```

### Using pip

```bash
pip install forwardemail-mcp
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
      "args": ["forwardemail-mcp"],
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
    "args": ["forwardemail-mcp"],
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

## Available Tools

### Account (3 tools)
| Tool | Description |
|------|-------------|
| `account_get` | Retrieve account information |
| `account_create` | Create a new account |
| `account_update` | Update account details |

### Domains (10 tools)
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
| `invite_accept` | Accept a domain invite |
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

## Usage Examples

### List Your Domains

Ask Claude: *"List my ForwardEmail domains"*

### Create an Email Alias

Ask Claude: *"Create an alias called 'support' on example.com that forwards to admin@gmail.com"*

### Send an Email

Ask Claude: *"Send an email from hello@example.com to user@gmail.com with subject 'Test' and body 'Hello!'"*

### Verify Domain Setup

Ask Claude: *"Verify the DNS records for example.com"*

## API Limitations

The following ForwardEmail API endpoints require **alias credentials** (email + generated password) instead of API token authentication and are **not supported** in this MCP server:

- Alias Contacts (CardDAV)
- Alias Calendars (CalDAV)
- Alias Messages (IMAP/POP3)
- Alias Folders (IMAP/POP3)

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

# Run tests
uv run pytest tests/ -v

# Run the server locally
FORWARDEMAIL_API_KEY="your_key" uv run python -m forwardemail_mcp
```

## How to Test

```bash
# Run unit tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=forwardemail_mcp

# Run single test file
uv run pytest tests/test_client.py -v
```

## How to Uninstall

```bash
# If installed via pip/uv
uv pip uninstall forwardemail-mcp

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
