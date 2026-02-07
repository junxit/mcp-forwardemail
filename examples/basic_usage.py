#!/usr/bin/env python3
"""Basic usage example for ForwardEmail MCP client.

This example demonstrates how to use the ForwardEmail API client directly.
For MCP tool usage, configure Claude Desktop with the server instead.
"""

import asyncio
import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from forwardemail_mcp.client import ForwardEmailClient


async def main():
    """Run basic API examples."""
    api_key = os.environ.get("FORWARDEMAIL_API_KEY")
    if not api_key:
        print("Error: FORWARDEMAIL_API_KEY environment variable is required")
        print("Get your API key from: https://forwardemail.net/my-account/security")
        sys.exit(1)
    
    async with ForwardEmailClient(api_key) as client:
        # Example 1: Get account info
        print("=== Account Info ===")
        try:
            account = await client.get_account()
            print(f"Email: {account.get('email')}")
            print(f"Plan: {account.get('plan')}")
        except Exception as e:
            print(f"Error getting account: {e}")
        
        # Example 2: List domains
        print("\n=== Domains ===")
        try:
            domains, pagination = await client.list_domains()
            if domains:
                for domain in domains[:5]:  # Show first 5
                    print(f"- {domain.get('name')} ({domain.get('plan')})")
                if pagination and pagination.item_count > 5:
                    print(f"  ... and {pagination.item_count - 5} more")
            else:
                print("No domains found")
        except Exception as e:
            print(f"Error listing domains: {e}")
        
        # Example 3: Check email limits
        print("\n=== Email Limits ===")
        try:
            limits = await client.get_email_limit()
            print(f"Sent today: {limits.get('count')} / {limits.get('limit')}")
        except Exception as e:
            print(f"Error getting limits: {e}")


if __name__ == "__main__":
    asyncio.run(main())
