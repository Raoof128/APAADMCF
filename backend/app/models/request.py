"""
Individual Request models
"""

import enum
from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, Enum, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base, TimestampMixin


class RequestType(str, enum.Enum):
    EXPLANATION = "explanation"
    HUMAN_REVIEW = "human_review"
    CORRECTION = "correction"
    ACCESS = "access"
    DELETION = "deletion"
    COMPLAINT = "complaint"


class RequestStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    PENDING_INFORMATION = "pending_information"
    COMPLETED = "completed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class IndividualRequest(Base, TimestampMixin):
    __tablename__ = "individual_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_type = Column(Enum(RequestType), nullable=False, index=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.SUBMITTED, index=True)

    # Requester Information (should be encrypted in production)
    requester_name = Column(String(255))
    requester_email = Column(String(255))
    requester_phone = Column(String(50))

    # Request Details
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id"), index=True)
    decision_reference = Column(String(255))
    decision_date = Column(Date)
    request_description = Column(Text)

    # Workflow
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    priority = Column(Integer, CheckConstraint('priority BETWEEN 1 AND 5'), default=3)

    # SLA Tracking
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    acknowledged_at = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Response
    response_summary = Column(Text)
    response_details = Column(Text)
    response_file_path = Column(String(500))

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="individual_requests")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_requests")
    history = relationship("RequestHistory", back_populates="request", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<IndividualRequest {self.request_type.value} ({self.status.value})>"


class RequestHistory(Base, TimestampMixin):
    __tablename__ = "request_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("individual_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(RequestStatus), nullable=False)
    notes = Column(Text)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    request = relationship("IndividualRequest", back_populates="history")

    def __repr__(self):
        return f"<RequestHistory {self.request_id} -> {self.status.value}>"
