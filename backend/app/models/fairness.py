"""
Fairness Assessment models
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Numeric, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base, TimestampMixin


class FairnessAssessment(Base, TimestampMixin):
    __tablename__ = "fairness_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    dataset_name = Column(String(255))
    dataset_size = Column(Integer)
    protected_attributes = Column(JSONB)  # array of protected attribute names

    # Fairness Metrics
    demographic_parity = Column(Numeric(5, 4))
    equal_opportunity = Column(Numeric(5, 4))
    predictive_parity = Column(Numeric(5, 4))
    error_rate_ratio = Column(Numeric(5, 4))
    statistical_parity_difference = Column(Numeric(5, 4))
    disparate_impact = Column(Numeric(5, 4))

    # Overall Assessment
    fairness_score = Column(Integer, CheckConstraint('fairness_score BETWEEN 0 AND 100'))
    is_high_risk = Column(Boolean, default=False)
    findings = Column(Text)
    recommendations = Column(Text)

    assessor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="fairness_assessments")
    explainability_results = relationship("ExplainabilityResult", back_populates="fairness_assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FairnessAssessment {self.adm_system_id} score={self.fairness_score}>"


class ExplainabilityResult(Base, TimestampMixin):
    __tablename__ = "explainability_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fairness_assessment_id = Column(UUID(as_uuid=True), ForeignKey("fairness_assessments.id", ondelete="CASCADE"), index=True)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(String(50))  # 'SHAP', 'LIME', etc.
    feature_importance = Column(JSONB)
    sample_explanations = Column(JSONB)
    visualization_path = Column(String(500))

    # Relationships
    fairness_assessment = relationship("FairnessAssessment", back_populates="explainability_results")
    adm_system = relationship("ADMSystem")

    def __repr__(self):
        return f"<ExplainabilityResult {self.method} for {self.adm_system_id}>"
