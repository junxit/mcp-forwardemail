"""ForwardEmail MCP Server.

An unofficial MCP (Model Context Protocol) server providing access to the
ForwardEmail API for Claude Desktop, Cline, and other MCP-compatible clients.

Typical usage example:

    # Configure in Claude Desktop
    # Add to ~/Library/Application Support/Claude/claude_desktop_config.json

    # Or run directly
    $ FORWARDEMAIL_API_KEY="your_key" forwardemail-mcp

Attributes:
    __version__: The current package version.
"""

__version__ = "0.4.1"

from .server import main

__all__ = ["main", "__version__"]
