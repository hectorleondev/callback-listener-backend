"""Utility functions for the application."""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


def is_valid_uuid(uuid_string: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def sanitize_path_id(path_id: str) -> str:
    """Sanitize a path ID to ensure it's URL-safe."""
    if not path_id:
        return str(uuid.uuid4())

    # Remove any characters that aren't alphanumeric, hyphens, or underscores
    sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "", path_id)

    # Ensure it's not empty after sanitization
    if not sanitized:
        return str(uuid.uuid4())

    return sanitized


def format_headers(headers: Dict[str, Any]) -> Dict[str, str]:
    """Format headers dictionary to ensure all values are strings."""
    formatted = {}
    for key, value in headers.items():
        if isinstance(value, (list, tuple)):
            formatted[key] = ", ".join(str(v) for v in value)
        else:
            formatted[key] = str(value)
    return formatted


def parse_content_type(content_type: Optional[str]) -> tuple:
    """Parse content type header into main type and charset."""
    if not content_type:
        return "text/plain", "utf-8"

    parts = content_type.split(";")
    main_type = parts[0].strip()

    charset = "utf-8"
    for part in parts[1:]:
        if "charset=" in part:
            charset = part.split("charset=")[1].strip()
            break

    return main_type, charset


def truncate_string(text: str, max_length: int = 1000) -> str:
    """Truncate a string to maximum length with ellipsis."""
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def get_client_ip(request_headers: Dict[str, str], remote_addr: str) -> str:
    """Extract client IP address considering proxy headers."""
    # Check for common proxy headers
    forwarded_for = request_headers.get("X-Forwarded-For", "")
    real_ip = request_headers.get("X-Real-IP", "")
    forwarded = request_headers.get("Forwarded", "")

    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()
    elif real_ip:
        return real_ip.strip()
    elif forwarded:
        # Parse Forwarded header (RFC 7239)
        match = re.search(r"for=([^;,\s]+)", forwarded)
        if match:
            return match.group(1).strip('"[]')

    return remote_addr or "unknown"


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string with timezone."""
    return dt.isoformat() + "Z" if dt else ""


def validate_pagination_params(limit: Any, offset: Any) -> tuple:
    """Validate and sanitize pagination parameters."""
    try:
        limit = int(limit) if limit is not None else 100
        offset = int(offset) if offset is not None else 0
    except (ValueError, TypeError):
        limit, offset = 100, 0

    # Ensure reasonable bounds
    limit = max(1, min(limit, 1000))  # Between 1 and 1000
    offset = max(0, offset)  # At least 0

    return limit, offset


def is_json_content_type(content_type: str) -> bool:
    """Check if content type indicates JSON data."""
    if not content_type:
        return False

    json_types = [
        "application/json",
        "application/ld+json",
        "application/hal+json",
        "text/json",
    ]

    main_type = content_type.split(";")[0].strip().lower()
    return main_type in json_types or main_type.endswith("+json")


def safe_json_loads(data: str) -> Any:
    """Safely parse JSON data with error handling."""
    import json

    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def mask_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Mask sensitive information in headers."""
    sensitive_headers = [
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "x-auth-token",
        "proxy-authorization",
    ]

    masked_headers = {}
    for key, value in headers.items():
        if key.lower() in sensitive_headers:
            masked_headers[key] = "***MASKED***"
        else:
            masked_headers[key] = value

    return masked_headers
