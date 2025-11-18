"""
Transparency Notice models
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class TransparencyNotice(Base, TimestampMixin):
    __tablename__ = "transparency_notices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adm_system_id = Column(UUID(as_uuid=True), ForeignKey("adm_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1)

    # APP5 Compliance Fields
    collection_notice = Column(Text)
    purpose_statement = Column(Text)
    data_usage_explanation = Column(Text)
    decision_explanation = Column(Text)
    rights_explanation = Column(Text)
    review_process_explanation = Column(Text)
    contact_information = Column(Text)

    # Metadata
    language = Column(String(10), default='en')
    is_active = Column(Boolean, default=True, index=True)
    published_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    adm_system = relationship("ADMSystem", back_populates="transparency_notices")

    def __repr__(self):
        return f"<TransparencyNotice v{self.version} for {self.adm_system_id}>"
