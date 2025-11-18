"""
ADM System models
"""

import enum
from sqlalchemy import Column, String, Text, Boolean, Date, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class ADMCategory(str, enum.Enum):
    FULLY_AUTOMATED = "fully_automated"
    PARTIALLY_AUTOMATED = "partially_automated"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"


class DecisionImpact(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SystemStatus(str, enum.Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    DECOMMISSIONED = "decommissioned"


class ADMSystem(Base, TimestampMixin):
    __tablename__ = "adm_systems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    purpose = Column(Text, nullable=False)
    adm_category = Column(Enum(ADMCategory), nullable=False)
    decision_impact = Column(Enum(DecisionImpact), nullable=False, index=True)
    system_status = Column(Enum(SystemStatus), default=SystemStatus.DEVELOPMENT, index=True)
    model_type = Column(String(100))
    deployment_date = Column(Date)
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    data_retention_period = Column(Integer)  # in days
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_adm_systems")
    data_categories = relationship("ADMSystemDataCategory", back_populates="adm_system", cascade="all, delete-orphan")
    pia_assessments = relationship("PIAAssessment", back_populates="adm_system", cascade="all, delete-orphan")
    risk_items = relationship("RiskItem", back_populates="adm_system", cascade="all, delete-orphan")
    fairness_assessments = relationship("FairnessAssessment", back_populates="adm_system", cascade="all, delete-orphan")
    individual_requests = relationship("IndividualRequest", back_populates="adm_system")
    compliance_alerts = relationship("ComplianceAlert", back_populates="adm_system", cascade="all, delete-orphan")
    drift_detections = relationship("DriftDetection", back_populates="adm_system", cascade="all, delete-orphan")
    transparency_notices = relationship("TransparencyNotice", back_populates="adm_system", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ADMSystem {self.name} ({self.decision_impact.value})>"


class ADMSystemDataCategory(Base, TimestampMixin):
    __tablename__ = "adm_system_data_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    data_category_id = Column(UUID(as_uuid=True), ForeignKey("data_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(Text)
    is_input = Column(Boolean, default=True)
    is_output = Column(Boolean, default=False)

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="data_categories")
    data_category = relationship("DataCategory", back_populates="adm_systems")

    def __repr__(self):
        return f"<ADMSystemDataCategory {self.adm_system_id} - {self.data_category_id}>"
