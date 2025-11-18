"""
Compliance Report models
"""

from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from .base import Base, TimestampMixin


class ComplianceReport(Base, TimestampMixin):
    __tablename__ = "compliance_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(String(100), index=True)  # 'oaic', 'internal', 'fairness_audit', etc.
    report_period_start = Column(Date)
    report_period_end = Column(Date)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_path = Column(String(500))
    file_format = Column(String(20))
    summary = Column(JSONB)
    metadata = Column(JSONB)

    def __repr__(self):
        return f"<ComplianceReport {self.report_type} ({self.report_period_start} - {self.report_period_end})>"
