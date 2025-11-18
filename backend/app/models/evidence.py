"""
Evidence Item models
"""

from sqlalchemy import Column, String, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class EvidenceItem(Base, TimestampMixin):
    __tablename__ = "evidence_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pia_assessment_id = Column(UUID(as_uuid=True), ForeignKey("pia_assessments.id", ondelete="CASCADE"), index=True)
    risk_item_id = Column(UUID(as_uuid=True), ForeignKey("risk_items.id", ondelete="CASCADE"), index=True)
    mitigation_task_id = Column(UUID(as_uuid=True), ForeignKey("mitigation_tasks.id", ondelete="CASCADE"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(BigInteger)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    metadata = Column(JSONB)

    # Relationships
    pia_assessment = relationship("PIAAssessment", back_populates="evidence_items")
    risk_item = relationship("RiskItem", back_populates="evidence_items")
    mitigation_task = relationship("MitigationTask", back_populates="evidence_items")

    def __repr__(self):
        return f"<EvidenceItem {self.title}>"
