"""
ADM System schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from ..models.adm_system import ADMCategory, DecisionImpact, SystemStatus


class ADMSystemBase(BaseModel):
    name: str
    description: Optional[str] = None
    purpose: str
    adm_category: ADMCategory
    decision_impact: DecisionImpact
    system_status: SystemStatus = SystemStatus.DEVELOPMENT
    model_type: Optional[str] = None
    deployment_date: Optional[date] = None
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    data_retention_period: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ADMSystemCreate(ADMSystemBase):
    owner_id: Optional[UUID] = None
    data_category_ids: Optional[List[UUID]] = []


class ADMSystemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    adm_category: Optional[ADMCategory] = None
    decision_impact: Optional[DecisionImpact] = None
    system_status: Optional[SystemStatus] = None
    model_type: Optional[str] = None
    deployment_date: Optional[date] = None
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    data_retention_period: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ADMSystemResponse(ADMSystemBase):
    id: UUID
    owner_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ADMSystemDetail(ADMSystemResponse):
    """Extended response with related data"""
    pia_count: int = 0
    risk_count: int = 0
    open_request_count: int = 0
    latest_fairness_score: Optional[int] = None
