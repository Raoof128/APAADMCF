"""
Audit Log models
"""

import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    action = Column(Enum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), index=True)  # 'adm_system', 'pia', 'request', etc.
    resource_id = Column(UUID(as_uuid=True), index=True)
    ip_address = Column(INET)
    user_agent = Column(Text)
    request_path = Column(String(500))
    request_method = Column(String(10))
    status_code = Column(Integer)
    changes = Column(JSONB)  # before/after values
    metadata = Column(JSONB)

    def __repr__(self):
        return f"<AuditLog {self.action.value} {self.resource_type} by {self.user_id}>"
