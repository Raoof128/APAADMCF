"""
PIA Assessment schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from ..models.pia import PIAStatus
from ..models.adm_system import DecisionImpact


class PIAAssessmentBase(BaseModel):
    purpose_description: Optional[str] = None
    necessity_justification: Optional[str] = None
    purpose_score: Optional[int] = Field(None, ge=0, le=100)
    data_minimisation_assessment: Optional[str] = None
    data_minimisation_score: Optional[int] = Field(None, ge=0, le=100)
    consent_mechanism: Optional[str] = None
    notification_method: Optional[str] = None
    consent_score: Optional[int] = Field(None, ge=0, le=100)
    reasonable_expectations_analysis: Optional[str] = None
    reasonable_expectations_score: Optional[int] = Field(None, ge=0, le=100)
    sensitive_info_used: Optional[bool] = None
    sensitive_info_justification: Optional[str] = None
    sensitive_info_score: Optional[int] = Field(None, ge=0, le=100)
    overall_risk_level: Optional[DecisionImpact] = None
    overall_score: Optional[int] = Field(None, ge=0, le=100)
    recommendations: Optional[str] = None


class PIAAssessmentCreate(PIAAssessmentBase):
    adm_system_id: UUID


class PIAAssessmentUpdate(PIAAssessmentBase):
    status: Optional[PIAStatus] = None


class PIAAssessmentResponse(PIAAssessmentBase):
    id: UUID
    adm_system_id: UUID
    version: int
    status: PIAStatus
    assessor_id: Optional[UUID] = None
    reviewer_id: Optional[UUID] = None
    approver_id: Optional[UUID] = None
    assessment_date: Optional[date] = None
    review_date: Optional[date] = None
    approval_date: Optional[date] = None
    next_review_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PIAApprovalRequest(BaseModel):
    approved: bool
    comments: Optional[str] = None
