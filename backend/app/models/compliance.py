"""
Compliance Monitoring models
"""

import enum
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base, TimestampMixin


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class ComplianceAlert(Base, TimestampMixin):
    __tablename__ = "compliance_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), index=True)
    alert_type = Column(String(100), index=True)  # 'drift', 'bias', 'policy_violation', etc.
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    metrics = Column(JSONB)
    threshold_value = Column(Numeric)
    actual_value = Column(Numeric)

    # Workflow
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="compliance_alerts")

    def __repr__(self):
        return f"<ComplianceAlert {self.title} ({self.severity.value})>"


class DriftDetection(Base, TimestampMixin):
    __tablename__ = "drift_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    detection_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    drift_type = Column(String(50), index=True)  # 'data', 'model', 'concept'
    drift_score = Column(Numeric(5, 4))
    baseline_metrics = Column(JSONB)
    current_metrics = Column(JSONB)
    features_affected = Column(JSONB)
    is_significant = Column(Boolean, default=False)
    notes = Column(Text)

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="drift_detections")

    def __repr__(self):
        return f"<DriftDetection {self.drift_type} for {self.adm_system_id}>"
