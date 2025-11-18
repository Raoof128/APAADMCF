"""
Privacy Impact Assessment models
"""

import enum
from sqlalchemy import Column, Text, Integer, Boolean, Date, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin
from .adm_system import DecisionImpact


class PIAStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"


class PIAAssessment(Base, TimestampMixin):
    __tablename__ = "pia_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1)
    status = Column(Enum(PIAStatus), default=PIAStatus.DRAFT, index=True)

    # Purpose & Necessity Test
    purpose_description = Column(Text)
    necessity_justification = Column(Text)
    purpose_score = Column(Integer, CheckConstraint('purpose_score BETWEEN 0 AND 100'))

    # Data Minimisation (APP3)
    data_minimisation_assessment = Column(Text)
    data_minimisation_score = Column(Integer, CheckConstraint('data_minimisation_score BETWEEN 0 AND 100'))

    # Consent/Notification (APP5)
    consent_mechanism = Column(Text)
    notification_method = Column(Text)
    consent_score = Column(Integer, CheckConstraint('consent_score BETWEEN 0 AND 100'))

    # Reasonable Expectations
    reasonable_expectations_analysis = Column(Text)
    reasonable_expectations_score = Column(Integer, CheckConstraint('reasonable_expectations_score BETWEEN 0 AND 100'))

    # Sensitive Information Test
    sensitive_info_used = Column(Boolean)
    sensitive_info_justification = Column(Text)
    sensitive_info_score = Column(Integer, CheckConstraint('sensitive_info_score BETWEEN 0 AND 100'))

    # Overall Assessment
    overall_risk_level = Column(Enum(DecisionImpact))
    overall_score = Column(Integer, CheckConstraint('overall_score BETWEEN 0 AND 100'))
    recommendations = Column(Text)

    # Approval
    assessor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assessment_date = Column(Date)
    review_date = Column(Date)
    approval_date = Column(Date)
    next_review_date = Column(Date)

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="pia_assessments")
    risk_items = relationship("RiskItem", back_populates="pia_assessment", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="pia_assessment")

    def __repr__(self):
        return f"<PIAAssessment {self.id} v{self.version} ({self.status.value})>"
