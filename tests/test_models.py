"""Tests for Path model."""

from datetime import datetime

import pytest

from app import db
from app.models.path import Path


class TestPathModel:
    """Test cases for Path model."""

    def test_path_creation(self, db_session):
        """Test creating a new path."""
        path = Path(path_id="test-path-123")
        db_session.add(path)
        db_session.commit()

        assert path.id is not None
        assert path.path_id == "test-path-123"
        assert path.created_at is not None
        assert path.updated_at is not None

    def test_path_auto_uuid_generation(self, db_session):
        """Test automatic UUID generation for path_id."""
        path = Path()
        db_session.add(path)
        db_session.commit()

        assert path.path_id is not None
        assert len(path.path_id) == 36  # UUID4 length

    def test_path_string_representation(self, db_session):
        """Test string representation of path."""
        path = Path(path_id="test-path-456")
        assert str(path) == "<Path test-path-456>"

    def test_path_to_dict(self, sample_path):
        """Test converting path to dictionary."""
        path_dict = sample_path.to_dict()

        assert "id" in path_dict
        assert "path_id" in path_dict
        assert "created_at" in path_dict
        assert "updated_at" in path_dict
        assert "request_count" in path_dict
        assert path_dict["path_id"] == "test-path-123"
        assert path_dict["request_count"] == 0

    def test_find_by_path_id(self, sample_path):
        """Test finding path by path_id."""
        found_path = Path.find_by_path_id("test-path-123")
        assert found_path is not None
        assert found_path.id == sample_path.id

        not_found = Path.find_by_path_id("non-existent")
        assert not_found is None

    def test_create_new_path(self, db_session):
        """Test creating new path class method."""
        path = Path.create_new_path("custom-path-id")

        assert path.path_id == "custom-path-id"
        assert path.id is not None

        # Test finding the created path
        found = Path.find_by_path_id("custom-path-id")
        assert found is not None

    def test_create_new_path_without_id(self, db_session):
        """Test creating new path without specifying ID."""
        path = Path.create_new_path()

        assert path.path_id is not None
        assert len(path.path_id) == 36  # UUID4 length
        assert path.id is not None

    def test_path_uniqueness(self, db_session):
        """Test that path_id must be unique."""
        Path.create_new_path("unique-path")

        with pytest.raises(Exception):  # Should raise integrity error
            Path.create_new_path("unique-path")
            db_session.commit()

    def test_path_relationship_with_requests(self, sample_path, sample_request):
        """Test relationship between path and requests."""
        assert len(sample_path.requests) == 1
        assert sample_path.requests[0] == sample_request
        assert sample_request.path == sample_path
