"""Tests for service layer."""

from unittest.mock import Mock, patch

import pytest

from app.models.path import Path
from app.models.request import Request
from app.services.webhook_service import PathService, RequestService


class TestPathService:
    """Test cases for PathService."""

    def test_create_path(self, db_session):
        """Test creating a path via service."""
        path = PathService.create_path()

        assert path is not None
        assert path.path_id is not None
        assert path.id is not None

    def test_create_path_with_custom_id(self, db_session):
        """Test creating path with custom ID via service."""
        custom_id = "service-test-path"
        path = PathService.create_path(custom_path_id=custom_id)

        assert path.path_id == custom_id

    def test_get_path_by_id(self, sample_path):
        """Test getting path by ID via service."""
        path = PathService.get_path_by_id(sample_path.path_id)

        assert path is not None
        assert path.id == sample_path.id

    def test_get_path_by_id_not_found(self):
        """Test getting non-existent path via service."""
        path = PathService.get_path_by_id("non-existent")
        assert path is None

    def test_get_path_statistics(self, sample_path, sample_request):
        """Test getting path statistics via service."""
        stats = PathService.get_path_statistics(sample_path.path_id)

        assert stats is not None
        assert stats["path_id"] == sample_path.path_id
        assert stats["total_requests"] == 1
        assert "POST" in stats["method_counts"]
        assert stats["method_counts"]["POST"] == 1

    def test_get_path_statistics_not_found(self):
        """Test getting statistics for non-existent path."""
        stats = PathService.get_path_statistics("non-existent")
        assert stats is None


class TestRequestService:
    """Test cases for RequestService."""

    def test_capture_request(self, sample_path, db_session):
        """Test capturing request via service."""
        # Mock Flask request
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.headers = {"Content-Type": "application/json"}
        mock_request.args = {"param": "value"}
        mock_request.data = b'{"test": "data"}'
        mock_request.environ = {"HTTP_X_FORWARDED_FOR": "192.168.1.1"}
        mock_request.remote_addr = "127.0.0.1"

        with patch(
            "app.models.request.Request.create_from_flask_request"
        ) as mock_create:
            mock_request_obj = Mock()
            mock_request_obj.id = "test-id"
            mock_create.return_value = mock_request_obj

            result = RequestService.capture_request(mock_request, sample_path.path_id)

            assert result == mock_request_obj
            mock_create.assert_called_once_with(mock_request, sample_path)

    def test_capture_request_path_not_found(self):
        """Test capturing request for non-existent path."""
        mock_request = Mock()

        with pytest.raises(ValueError, match="Path .* not found"):
            RequestService.capture_request(mock_request, "non-existent")

    def test_get_requests_for_path(self, sample_path, sample_request):
        """Test getting requests for path via service."""
        requests = RequestService.get_requests_for_path(sample_path.path_id)

        assert len(requests) == 1
        assert requests[0].id == sample_request.id

    def test_get_requests_for_path_with_filter(self, sample_path, sample_request):
        """Test getting requests with method filter."""
        requests = RequestService.get_requests_for_path(
            sample_path.path_id, method_filter="POST"
        )

        assert len(requests) == 1
        assert requests[0].method == "POST"

        # Test with non-matching filter
        requests = RequestService.get_requests_for_path(
            sample_path.path_id, method_filter="GET"
        )

        assert len(requests) == 0

    def test_get_requests_for_path_pagination(self, sample_path):
        """Test pagination for requests."""
        requests = RequestService.get_requests_for_path(
            sample_path.path_id, limit=5, offset=0
        )

        assert isinstance(requests, list)

    def test_get_request_by_id(self, sample_path, sample_request):
        """Test getting specific request by ID."""
        request = RequestService.get_request_by_id(
            str(sample_request.id), sample_path.path_id
        )

        assert request is not None
        assert request.id == sample_request.id

    def test_get_request_by_id_not_found(self, sample_path):
        """Test getting non-existent request."""
        import uuid

        fake_id = str(uuid.uuid4())

        request = RequestService.get_request_by_id(fake_id, sample_path.path_id)
        assert request is None

    @patch("app.services.webhook_service.db.session")
    def test_delete_old_requests(self, mock_session):
        """Test deleting old requests."""
        mock_query = Mock()
        mock_query.filter.return_value.delete.return_value = 5

        with patch("app.models.request.Request.query", mock_query):
            deleted_count = RequestService.delete_old_requests(days_old=30)

            assert deleted_count == 5
            mock_session.commit.assert_called_once()
