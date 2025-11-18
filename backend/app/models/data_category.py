"""
Data Category models
"""

import enum
from sqlalchemy import Column, String, Text, Boolean, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class DataSensitivity(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SENSITIVE = "sensitive"  # Under Privacy Act
    HIGHLY_SENSITIVE = "highly_sensitive"


class DataCategory(Base, TimestampMixin):
    __tablename__ = "data_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sensitivity = Column(Enum(DataSensitivity), nullable=False)
    is_pii = Column(Boolean, default=False)
    is_sensitive_info = Column(Boolean, default=False)  # Under Privacy Act
    legal_basis = Column(Text)
    retention_period = Column(Integer)  # in days

    # Relationships
    adm_systems = relationship("ADMSystemDataCategory", back_populates="data_category")

    def __repr__(self):
        return f"<DataCategory {self.name} ({self.sensitivity.value})>"
