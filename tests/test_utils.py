"""Tests for utility functions."""

import uuid
from datetime import datetime

import pytest

from app.utils.helpers import (
    format_headers,
    format_timestamp,
    get_client_ip,
    is_json_content_type,
    is_valid_uuid,
    mask_sensitive_headers,
    parse_content_type,
    safe_json_loads,
    sanitize_path_id,
    truncate_string,
    validate_pagination_params,
)


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_is_valid_uuid(self):
        """Test UUID validation."""
        valid_uuid = str(uuid.uuid4())
        assert is_valid_uuid(valid_uuid) is True

        invalid_uuids = ["not-a-uuid", "123", "", None, "invalid-uuid-format"]
        for invalid in invalid_uuids:
            assert is_valid_uuid(invalid) is False

    def test_sanitize_path_id(self):
        """Test path ID sanitization."""
        # Valid path IDs should remain unchanged
        assert sanitize_path_id("valid-path-123") == "valid-path-123"
        assert sanitize_path_id("valid_path_456") == "valid_path_456"

        # Invalid characters should be removed
        sanitized = sanitize_path_id("path@with#special$chars!")
        assert "@" not in sanitized
        assert "#" not in sanitized
        assert "$" not in sanitized
        assert "!" not in sanitized

        # Empty or None should generate UUID
        result = sanitize_path_id("")
        assert len(result) == 36  # UUID length

        result = sanitize_path_id(None)
        assert len(result) == 36

    def test_format_headers(self):
        """Test header formatting."""
        headers = {
            "Content-Type": "application/json",
            "Accept": ["application/json", "text/html"],
            "Custom-Header": 123,
        }

        formatted = format_headers(headers)

        assert formatted["Content-Type"] == "application/json"
        assert formatted["Accept"] == "application/json, text/html"
        assert formatted["Custom-Header"] == "123"

    def test_parse_content_type(self):
        """Test content type parsing."""
        # Standard content type
        main_type, charset = parse_content_type("application/json; charset=utf-8")
        assert main_type == "application/json"
        assert charset == "utf-8"

        # Without charset
        main_type, charset = parse_content_type("text/plain")
        assert main_type == "text/plain"
        assert charset == "utf-8"  # Default

        # None content type
        main_type, charset = parse_content_type(None)
        assert main_type == "text/plain"
        assert charset == "utf-8"

    def test_truncate_string(self):
        """Test string truncation."""
        short_string = "short"
        assert truncate_string(short_string, 100) == "short"

        long_string = "a" * 1000
        truncated = truncate_string(long_string, 50)
        assert len(truncated) == 50
        assert truncated.endswith("...")

        # None or empty string
        assert truncate_string(None) is None
        assert truncate_string("") == ""

    def test_get_client_ip(self):
        """Test client IP extraction."""
        headers = {}

        # Direct remote address
        ip = get_client_ip(headers, "192.168.1.1")
        assert ip == "192.168.1.1"

        # X-Forwarded-For header
        headers["X-Forwarded-For"] = "203.0.113.1, 192.168.1.1"
        ip = get_client_ip(headers, "127.0.0.1")
        assert ip == "203.0.113.1"

        # X-Real-IP header
        headers = {"X-Real-IP": "203.0.113.2"}
        ip = get_client_ip(headers, "127.0.0.1")
        assert ip == "203.0.113.2"

        # Forwarded header (RFC 7239)
        headers = {"Forwarded": "for=203.0.113.3;proto=https"}
        ip = get_client_ip(headers, "127.0.0.1")
        assert ip == "203.0.113.3"

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        formatted = format_timestamp(dt)
        assert formatted == "2023-01-01T12:00:00Z"

        # None datetime
        assert format_timestamp(None) == ""

    def test_validate_pagination_params(self):
        """Test pagination parameter validation."""
        # Valid parameters
        limit, offset = validate_pagination_params(50, 10)
        assert limit == 50
        assert offset == 10

        # Invalid parameters should use defaults
        limit, offset = validate_pagination_params("invalid", "invalid")
        assert limit == 100
        assert offset == 0

        # None parameters should use defaults
        limit, offset = validate_pagination_params(None, None)
        assert limit == 100
        assert offset == 0

        # Boundary testing
        limit, offset = validate_pagination_params(2000, -5)
        assert limit == 1000  # Max limit
        assert offset == 0  # Min offset

    def test_is_json_content_type(self):
        """Test JSON content type detection."""
        json_types = [
            "application/json",
            "application/ld+json",
            "application/hal+json",
            "text/json",
            "application/vnd.api+json",
        ]

        for content_type in json_types:
            assert is_json_content_type(content_type) is True

        non_json_types = [
            "text/html",
            "application/xml",
            "text/plain",
            "image/png",
            None,
            "",
        ]

        for content_type in non_json_types:
            assert is_json_content_type(content_type) is False

    def test_safe_json_loads(self):
        """Test safe JSON parsing."""
        # Valid JSON
        data = safe_json_loads('{"key": "value"}')
        assert data == {"key": "value"}

        # Invalid JSON
        assert safe_json_loads("invalid json") is None
        assert safe_json_loads(None) is None
        assert safe_json_loads("") is None

    def test_mask_sensitive_headers(self):
        """Test masking of sensitive headers."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token",
            "Cookie": "session=abc123",
            "X-API-Key": "secret-key",
            "User-Agent": "Mozilla/5.0",
        }

        masked = mask_sensitive_headers(headers)

        assert masked["Content-Type"] == "application/json"
        assert masked["User-Agent"] == "Mozilla/5.0"
        assert masked["Authorization"] == "***MASKED***"
        assert masked["Cookie"] == "***MASKED***"
        assert masked["X-API-Key"] == "***MASKED***"
