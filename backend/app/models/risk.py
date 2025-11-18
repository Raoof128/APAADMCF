"""
Risk Item models
"""

import enum
from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, Enum, CheckConstraint, Computed
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    ASSESSING = "assessing"
    MITIGATING = "mitigating"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class RiskItem(Base, TimestampMixin):
    __tablename__ = "risk_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pia_assessment_id = Column(UUID(as_uuid=True), ForeignKey("pia_assessments.id", ondelete="CASCADE"), index=True)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    risk_category = Column(String(100))  # 'bias', 'privacy', 'security', 'fairness', etc.
    severity = Column(Enum(RiskSeverity), nullable=False, index=True)
    likelihood = Column(Integer, CheckConstraint('likelihood BETWEEN 1 AND 5'))
    impact = Column(Integer, CheckConstraint('impact BETWEEN 1 AND 5'))
    # risk_score is computed as likelihood * impact
    risk_score = Column(Integer)
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    identified_date = Column(Date)
    target_closure_date = Column(Date)
    actual_closure_date = Column(Date)

    # Relationships
    pia_assessment = relationship("PIAAssessment", back_populates="risk_items")
    adm_system = relationship("ADMSystem", back_populates="risk_items")
    mitigation_tasks = relationship("MitigationTask", back_populates="risk_item", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="risk_item")

    def __repr__(self):
        return f"<RiskItem {self.title} ({self.severity.value})>"
