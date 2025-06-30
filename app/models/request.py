"""Request model for storing captured webhook requests."""

import json
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app import db


class Request(db.Model):
    """Model for captured webhook requests."""

    __tablename__ = "requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    path_id = Column(
        String(36), ForeignKey("paths.id"), nullable=False, index=True
    )

    # Request details
    method = Column(String(10), nullable=False)
    headers = Column(Text, nullable=False, default='{}')  # Store as JSON string for SQLite
    body = Column(Text, nullable=True)
    query_params = Column(Text, nullable=False, default='{}')  # Store as JSON string for SQLite

    # Client information
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship to path
    path = relationship("Path", back_populates="requests")

    def __repr__(self):
        """String representation of the Request."""
        return (
            f'<Request {self.method} {self.path.path_id if self.path else "Unknown"}>'
        )

    @property
    def headers_dict(self):
        """Get headers as dictionary."""
        try:
            return json.loads(self.headers) if self.headers else {}
        except json.JSONDecodeError:
            return {}

    @headers_dict.setter
    def headers_dict(self, value):
        """Set headers from dictionary."""
        self.headers = json.dumps(value) if value else '{}'

    @property
    def query_params_dict(self):
        """Get query params as dictionary."""
        try:
            return json.loads(self.query_params) if self.query_params else {}
        except json.JSONDecodeError:
            return {}

    @query_params_dict.setter
    def query_params_dict(self, value):
        """Set query params from dictionary."""
        self.query_params = json.dumps(value) if value else '{}'

    def to_dict(self, include_body=True):
        """Convert the Request to a dictionary."""
        result = {
            "id": str(self.id),
            "path_id": str(self.path_id),
            "method": self.method,
            "headers": self.headers_dict,
            "query_params": self.query_params_dict,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

        if include_body:
            result["body"] = self.body

        return result

    @classmethod
    def create_from_flask_request(cls, flask_request, path_instance):
        """Create a Request instance from a Flask request object."""
        # Extract headers as dict, excluding problematic headers
        headers = {}
        for key, value in flask_request.headers:
            if key.lower() not in ["content-length", "host"]:
                headers[key] = value

        # Extract query parameters
        query_params = dict(flask_request.args)

        # Get request body
        body = None
        if flask_request.data:
            try:
                body = flask_request.data.decode("utf-8")
            except UnicodeDecodeError:
                body = f"<Binary data: {len(flask_request.data)} bytes>"

        # Get client IP (considering proxies)
        ip_address = flask_request.environ.get(
            "HTTP_X_FORWARDED_FOR", flask_request.remote_addr
        )
        if ip_address and "," in ip_address:
            ip_address = ip_address.split(",")[0].strip()

        request = cls(
            path_id=path_instance.id,
            method=flask_request.method,
            body=body,
            ip_address=ip_address,
            user_agent=flask_request.headers.get("User-Agent", ""),
        )
        
        # Set JSON data using properties
        request.headers_dict = headers
        request.query_params_dict = query_params

        db.session.add(request)
        db.session.commit()
        return request

    @classmethod
    def get_by_path_id(cls, path_id, limit=100, offset=0):
        """Get requests for a specific path with pagination."""
        from app.models.path import Path

        path = Path.find_by_path_id(path_id)
        if not path:
            return []

        return (
            cls.query.filter_by(path_id=path.id)
            .order_by(cls.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    @classmethod
    def get_by_id_and_path(cls, request_id, path_id):
        """Get a specific request by ID and path ID."""
        from app.models.path import Path

        path = Path.find_by_path_id(path_id)
        if not path:
            return None

        return cls.query.filter_by(id=request_id, path_id=path.id).first()

    @classmethod
    def get_recent_requests(cls, limit=10):
        """Get the most recent requests across all paths."""
        return (
            cls.query
            .order_by(cls.timestamp.desc())
            .limit(limit)
            .all()
        )
