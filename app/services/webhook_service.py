"""Service layer for business logic."""

import structlog

from app import db
from app.models.path import Path
from app.models.request import Request

logger = structlog.get_logger()


class PathService:
    """Service for path-related operations."""

    @staticmethod
    def create_path(custom_path_id=None):
        """Create a new webhook path."""
        try:
            path = Path.create_new_path(path_id=custom_path_id)
            logger.info("Path created via service", path_id=path.path_id)
            return path
        except Exception as e:
            logger.error("Error creating path in service", error=str(e))
            raise

    @staticmethod
    def get_path_by_id(path_id):
        """Get a path by its ID."""
        return Path.find_by_path_id(path_id)

    @staticmethod
    def get_path_statistics(path_id):
        """Get statistics for a path."""
        path = Path.find_by_path_id(path_id)
        if not path:
            return None

        total_requests = len(path.requests) if path.requests else 0

        # Count by method
        method_counts = {}
        if path.requests:
            for request in path.requests:
                method = request.method
                method_counts[method] = method_counts.get(method, 0) + 1

        return {
            "path_id": path.path_id,
            "total_requests": total_requests,
            "method_counts": method_counts,
            "created_at": path.created_at.isoformat() if path.created_at else None,
            "last_request": path.requests[0].timestamp.isoformat()
            if path.requests
            else None,
        }


class RequestService:
    """Service for request-related operations."""

    @staticmethod
    def capture_request(flask_request, path_id):
        """Capture a webhook request."""
        try:
            path = Path.find_by_path_id(path_id)
            if not path:
                raise ValueError(f"Path {path_id} not found")

            request_record = Request.create_from_flask_request(flask_request, path)
            logger.info(
                "Request captured via service",
                path_id=path_id,
                request_id=str(request_record.id),
            )
            return request_record
        except Exception as e:
            logger.error(
                "Error capturing request in service", path_id=path_id, error=str(e)
            )
            raise

    @staticmethod
    def get_requests_for_path(path_id, limit=100, offset=0, method_filter=None):
        """Get requests for a path with optional filtering."""
        path = Path.find_by_path_id(path_id)
        if not path:
            return []

        query = Request.query.filter_by(path_id=path.id)

        if method_filter:
            query = query.filter(Request.method == method_filter.upper())

        requests = (
            query.order_by(Request.timestamp.desc()).limit(limit).offset(offset).all()
        )

        return requests

    @staticmethod
    def get_request_by_id(request_id, path_id):
        """Get a specific request by ID and path."""
        return Request.get_by_id_and_path(request_id, path_id)

    @staticmethod
    def delete_old_requests(days_old=30):
        """Delete requests older than specified days."""
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        try:
            deleted_count = Request.query.filter(
                Request.timestamp < cutoff_date
            ).delete()
            db.session.commit()
            logger.info(
                "Old requests deleted",
                count=deleted_count,
                cutoff_date=cutoff_date.isoformat(),
            )
            return deleted_count
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting old requests", error=str(e))
            raise
