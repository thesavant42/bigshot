"""
Database models for the bigshot application
"""

import json
from datetime import datetime, UTC
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
    fetched_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

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


class User(db.Model):
    """User model for authentication and user management"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation"""
        result = {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            result["password_hash"] = self.password_hash

        return result


class LLMProviderConfig(db.Model):
    """LLM provider configuration model for runtime provider switching"""

    __tablename__ = "llm_provider_configs"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(
        db.String(50), nullable=False
    )  # 'openai', 'lmstudio', 'custom'
    name = db.Column(db.String(100), nullable=False)  # Display name
    base_url = db.Column(db.String(500), nullable=False)
    api_key = db.Column(db.Text)  # Can be null for providers that don't need keys
    model = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Only one can be active
    is_default = db.Column(db.Boolean, default=False)  # System default
    connection_timeout = db.Column(db.Integer, default=30)
    max_tokens = db.Column(db.Integer, default=4000)
    temperature = db.Column(db.Float, default=0.7)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    __table_args__ = (db.UniqueConstraint("name", name="unique_provider_name"),)

    def to_dict(self, include_sensitive=False):
        """Convert LLM provider config to dictionary representation"""
        result = {
            "id": self.id,
            "provider": self.provider,
            "name": self.name,
            "base_url": self.base_url,
            "model": self.model,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "connection_timeout": self.connection_timeout,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive and self.api_key:
            result["api_key"] = self.api_key
        elif self.api_key:
            # Mask the key for security
            result["api_key_masked"] = (
                self.api_key[:8] + "..." if len(self.api_key) > 8 else "***"
            )
        else:
            result["api_key_masked"] = None

        return result


class LLMProviderAuditLog(db.Model):
    """Audit log for LLM provider configuration changes"""

    __tablename__ = "llm_provider_audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    provider_config_id = db.Column(
        db.Integer, db.ForeignKey("llm_provider_configs.id"), nullable=True
    )
    action = db.Column(
        db.String(50), nullable=False
    )  # 'created', 'updated', 'activated', 'tested'
    old_values = db.Column(db.Text)  # JSON string of old values
    new_values = db.Column(db.Text)  # JSON string of new values
    test_result = db.Column(db.Text)  # JSON string of test results
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    provider_config = db.relationship("LLMProviderConfig", backref="audit_logs")
    user = db.relationship("User", backref="llm_provider_actions")

    def to_dict(self):
        """Convert audit log to dictionary representation"""
        return {
            "id": self.id,
            "provider_config_id": self.provider_config_id,
            "action": self.action,
            "old_values": json.loads(self.old_values) if self.old_values else None,
            "new_values": json.loads(self.new_values) if self.new_values else None,
            "test_result": json.loads(self.test_result) if self.test_result else None,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
