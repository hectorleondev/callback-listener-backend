"""Test configuration and fixtures."""

import os

import pytest

from app import create_app, db
from app.models.path import Path
from app.models.request import Request


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app("testing")

    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        # Clean up
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        # Start a transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Configure session to use the transaction
        db.session.configure(bind=connection)

        yield db.session

        # Rollback transaction
        transaction.rollback()
        connection.close()


@pytest.fixture
def sample_path(db_session):
    """Create a sample path for testing."""
    path = Path(path_id="test-path-123")
    db_session.add(path)
    db_session.commit()
    return path


@pytest.fixture
def sample_request(db_session, sample_path):
    """Create a sample request for testing."""
    from datetime import datetime

    request = Request(
        path_id=sample_path.id,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "Test Client"},
        body='{"test": "data"}',
        query_params={"param1": "value1"},
        ip_address="127.0.0.1",
        user_agent="Test Client",
        timestamp=datetime.utcnow(),
    )
    db_session.add(request)
    db_session.commit()
    return request


@pytest.fixture
def auth_headers():
    """Headers for authenticated requests."""
    return {"Content-Type": "application/json", "Accept": "application/json"}
