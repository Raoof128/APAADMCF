"""
User models
"""

import enum
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PRIVACY_OFFICER = "privacy_officer"
    COMPLIANCE_AUDITOR = "compliance_auditor"
    DATA_SCIENTIST = "data_scientist"
    INDIVIDUAL_REQUEST_MANAGER = "individual_request_manager"
    READ_ONLY_VIEWER = "read_only_viewer"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))

    # Relationships
    owned_adm_systems = relationship("ADMSystem", foreign_keys="ADMSystem.owner_id", back_populates="owner")
    assigned_requests = relationship("IndividualRequest", foreign_keys="IndividualRequest.assigned_to", back_populates="assignee")
    assigned_mitigation_tasks = relationship("MitigationTask", foreign_keys="MitigationTask.assigned_to", back_populates="assignee")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
