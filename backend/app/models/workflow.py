"""
Workflow models
"""

import enum
from sqlalchemy import Column, String, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Workflow(Base, TimestampMixin):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_type = Column(String(100), index=True)  # 'pia_approval', 'annual_review', etc.
    entity_type = Column(String(100), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, index=True)
    current_step = Column(String(100))
    steps = Column(JSONB)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    metadata = Column(JSONB)

    def __repr__(self):
        return f"<Workflow {self.workflow_type} ({self.status.value})>"
