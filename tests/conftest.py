"""Pytest fixtures for ForwardEmail MCP tests."""

import pytest


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def alias_creds():
    """Provide mock alias credentials (username, password) for testing."""
    return ("alias@example.com", "secretpass")
