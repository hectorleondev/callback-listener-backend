"""Tests for API endpoints."""

import json

import pytest

from app.models.path import Path
from app.models.request import Request


class TestPathsAPI:
    """Test cases for paths API endpoints."""

    def test_create_path_success(self, client, auth_headers):
        """Test successful path creation."""
        response = client.post("/api/paths", headers=auth_headers, data=json.dumps({}))

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "path_id" in data["data"]
        assert "id" in data["data"]

    def test_create_path_with_custom_id(self, client, auth_headers):
        """Test path creation with custom ID."""
        custom_id = "my-custom-webhook"
        response = client.post(
            "/api/paths", headers=auth_headers, data=json.dumps({"path_id": custom_id})
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["data"]["path_id"] == custom_id

    def test_get_path_logs_success(self, client, sample_path, sample_request):
        """Test retrieving path logs."""
        response = client.get(f"/api/paths/{sample_path.path_id}/logs")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "requests" in data["data"]
        assert len(data["data"]["requests"]) == 1
        assert data["data"]["requests"][0]["method"] == "POST"

    def test_get_path_logs_not_found(self, client):
        """Test retrieving logs for non-existent path."""
        response = client.get("/api/paths/non-existent-path/logs")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_get_path_logs_pagination(self, client, sample_path):
        """Test pagination for path logs."""
        response = client.get(
            f"/api/paths/{sample_path.path_id}/logs?limit=10&offset=0"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "pagination" in data["data"]
        assert data["data"]["pagination"]["limit"] == 10
        assert data["data"]["pagination"]["offset"] == 0

    def test_get_specific_request(self, client, sample_path, sample_request):
        """Test retrieving specific request."""
        response = client.get(
            f"/api/paths/{sample_path.path_id}/logs/{sample_request.id}"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["id"] == str(sample_request.id)
        assert data["data"]["method"] == "POST"

    def test_get_specific_request_not_found(self, client, sample_path):
        """Test retrieving non-existent request."""
        import uuid

        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/paths/{sample_path.path_id}/logs/{fake_id}")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False


class TestWebhooksAPI:
    """Test cases for webhook capture endpoints."""

    def test_capture_get_request(self, client, sample_path):
        """Test capturing a GET request."""
        response = client.get(f"/webhook/{sample_path.path_id}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert data["data"]["method"] == "GET"

    def test_capture_post_request_with_data(self, client, sample_path):
        """Test capturing a POST request with JSON data."""
        test_data = {"key": "value", "number": 42}
        response = client.post(
            f"/webhook/{sample_path.path_id}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["method"] == "POST"

    def test_capture_request_with_query_params(self, client, sample_path):
        """Test capturing request with query parameters."""
        response = client.get(
            f"/webhook/{sample_path.path_id}?param1=value1&param2=value2"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_capture_different_http_methods(self, client, sample_path):
        """Test capturing different HTTP methods."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        for method in methods:
            response = client.open(f"/webhook/{sample_path.path_id}", method=method)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["data"]["method"] == method

    def test_capture_request_non_existent_path(self, client):
        """Test capturing request to non-existent path."""
        response = client.get("/webhook/non-existent-path")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_capture_request_saves_to_database(self, client, sample_path, db_session):
        """Test that captured requests are saved to database."""
        initial_count = Request.query.filter_by(path_id=sample_path.id).count()

        response = client.post(
            f"/webhook/{sample_path.path_id}",
            headers={"Custom-Header": "test-value"},
            data="test body content",
        )

        assert response.status_code == 200

        # Check that request was saved
        final_count = Request.query.filter_by(path_id=sample_path.id).count()
        assert final_count == initial_count + 1

        # Verify request details
        saved_request = (
            Request.query.filter_by(path_id=sample_path.id)
            .order_by(Request.timestamp.desc())
            .first()
        )
        assert saved_request.method == "POST"
        assert saved_request.body == "test body content"
        assert "Custom-Header" in saved_request.headers


class TestHealthAPI:
    """Test cases for health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health/")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "callback-listener-backend"

    def test_readiness_check(self, client):
        """Test readiness check."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ready"
        assert data["database"] == "connected"

    def test_liveness_check(self, client):
        """Test liveness check."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "alive"
