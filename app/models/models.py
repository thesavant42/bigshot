"""
Database models for the bigshot application
"""

import json
from datetime import datetime, timezone
from app import db


class Domain(db.Model):
    """Domain model for hierarchical subdomain storage"""

    __tablename__ = "domains"

    id = db.Column(db.Integer, primary_key=True)
    root_domain = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.Text, default="")
    cdx_indexed = db.Column(db.Boolean, default=False)
    fetched_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint("subdomain", "source", name="unique_subdomain_source"),
    )

    def to_dict(self):
        """Convert domain to dictionary representation"""
        return {
            "id": self.id,
            "root_domain": self.root_domain,
            "subdomain": self.subdomain,
            "source": self.source,
            "tags": self.tags.split(",") if self.tags else [],
            "cdx_indexed": self.cdx_indexed,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Job(db.Model):
    """Job model for background task management"""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(255))
    status = db.Column(db.String(50), default="pending")
    progress = db.Column(db.Integer, default=0)
    result = db.Column(db.Text)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert job to dictionary representation"""
        return {
            "id": self.id,
            "type": self.type,
            "domain": self.domain,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class URL(db.Model):
    """URL model for storing discovered URLs"""

    __tablename__ = "urls"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, unique=True, nullable=False)
    domain = db.Column(db.String(255))
    timestamp = db.Column(db.String(50))
    status_code = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    tags = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert URL to dictionary representation"""
        return {
            "id": self.id,
            "url": self.url,
            "domain": self.domain,
            "timestamp": self.timestamp,
            "status_code": self.status_code,
            "mime_type": self.mime_type,
            "tags": self.tags.split(",") if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Note(db.Model):
    """Note model for URL-specific annotations"""

    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey("urls.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    url = db.relationship("URL", backref=db.backref("notes", lazy=True))

    def to_dict(self):
        """Convert note to dictionary representation"""
        return {
            "id": self.id,
            "url_id": self.url_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class APIKey(db.Model):
    """API key model for storing external service credentials"""

    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), unique=True, nullable=False)
    key_value = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self, include_key=False):
        """Convert API key to dictionary representation"""
        result = {
            "id": self.id,
            "service": self.service,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_key:
            result["key_value"] = self.key_value
        else:
            # Mask the key for security
            result["key_masked"] = (
                self.key_value[:8] + "..." if len(self.key_value) > 8 else "***"
            )

        return result


class Conversation(db.Model):
    """Conversation model for storing chat sessions"""

    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = db.relationship(
        "ChatMessage", backref="conversation", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert conversation to dictionary representation"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": len(self.messages),
        }


class ChatMessage(db.Model):
    """Chat message model for storing individual messages"""

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversations.id"), nullable=False
    )
    role = db.Column(db.String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    function_calls = db.Column(db.Text)  # JSON string of function calls
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert message to dictionary representation"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "function_calls": (
                json.loads(self.function_calls) if self.function_calls else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
