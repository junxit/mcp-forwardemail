"""Tests for ForwardEmail API client."""

import pytest
from forwardemail_mcp.client import ForwardEmailClient, PaginationInfo


class TestForwardEmailClient:
    """Tests for the ForwardEmailClient class."""

    def test_client_initialization(self, mock_api_key):
        """Test client initializes with API key.
        
        Args:
            mock_api_key: Fixture providing a mock API key.
        """
        client = ForwardEmailClient(mock_api_key)
        assert client.api_key == mock_api_key
        assert client._client is None

    def test_base_url(self, mock_api_key):
        """Test client has correct base URL.
        
        Args:
            mock_api_key: Fixture providing a mock API key.
        """
        client = ForwardEmailClient(mock_api_key)
        assert client.BASE_URL == "https://api.forwardemail.net"


class TestPaginationInfo:
    """Tests for PaginationInfo model."""

    def test_default_values(self):
        """Test PaginationInfo has correct defaults."""
        pagination = PaginationInfo()
        assert pagination.page_count == 0
        assert pagination.page_current == 1
        assert pagination.page_size == 10
        assert pagination.item_count == 0

    def test_custom_values(self):
        """Test PaginationInfo accepts custom values."""
        pagination = PaginationInfo(
            page_count=5,
            page_current=2,
            page_size=25,
            item_count=125,
        )
        assert pagination.page_count == 5
        assert pagination.page_current == 2
        assert pagination.page_size == 25
        assert pagination.item_count == 125
