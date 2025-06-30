"""API package initialization."""

from app.api.health import health_bp
from app.api.paths import paths_bp
from app.api.webhooks import webhooks_bp

__all__ = ["paths_bp", "webhooks_bp", "health_bp"]
