"""
Mitigation Task models
"""

import enum
from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class MitigationStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class MitigationTask(Base, TimestampMixin):
    __tablename__ = "mitigation_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_item_id = Column(UUID(as_uuid=True), ForeignKey("risk_items.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(MitigationStatus), default=MitigationStatus.PLANNED, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    priority = Column(Integer, CheckConstraint('priority BETWEEN 1 AND 5'))
    due_date = Column(Date)
    completion_date = Column(Date)
    effort_estimate = Column(Integer)  # in hours
    actual_effort = Column(Integer)  # in hours
    notes = Column(Text)

    # Relationships
    risk_item = relationship("RiskItem", back_populates="mitigation_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_mitigation_tasks")
    evidence_items = relationship("EvidenceItem", back_populates="mitigation_task")

    def __repr__(self):
        return f"<MitigationTask {self.title} ({self.status.value})>"
