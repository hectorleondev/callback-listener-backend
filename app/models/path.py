"""Path model for storing webhook paths."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from app import db


class Path(db.Model):
    """Model for webhook paths."""

    __tablename__ = "paths"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    path_id = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship to requests
    requests = relationship(
        "Request", back_populates="path", cascade="all, delete-orphan"
    )

    def __init__(self, path_id=None):
        """Initialize a new Path instance."""
        self.path_id = path_id or str(uuid.uuid4())

    def __repr__(self):
        """String representation of the Path."""
        return f"<Path {self.path_id}>"

    def to_dict(self):
        """Convert the Path to a dictionary."""
        return {
            "id": str(self.id),
            "path_id": self.path_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "request_count": len(self.requests) if self.requests else 0,
        }

    @classmethod
    def find_by_path_id(cls, path_id):
        """Find a path by its path_id."""
        return cls.query.filter_by(path_id=path_id).first()

    @classmethod
    def create_new_path(cls, path_id=None):
        """Create a new path with optional custom path_id."""
        path = cls(path_id=path_id)
        db.session.add(path)
        db.session.commit()
        return path

    @classmethod
    def get_all_paths(cls):
        """Get all paths ordered by creation date."""
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def count_all(cls):
        """Get the total count of all paths."""
        return cls.query.count()

    def delete(self):
        """Delete this path and all associated requests."""
        db.session.delete(self)
        db.session.commit()

    @property
    def request_count(self):
        """Get the count of requests for this path."""
        return len(self.requests) if self.requests else 0
