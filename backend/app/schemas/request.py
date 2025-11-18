"""
Individual Request schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from ..models.request import RequestType, RequestStatus


class IndividualRequestBase(BaseModel):
    request_type: RequestType
    requester_name: str
    requester_email: EmailStr
    requester_phone: Optional[str] = None
    adm_system_id: Optional[UUID] = None
    decision_reference: Optional[str] = None
    decision_date: Optional[date] = None
    request_description: str


class IndividualRequestCreate(IndividualRequestBase):
    pass


class IndividualRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    assigned_to: Optional[UUID] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    response_summary: Optional[str] = None
    response_details: Optional[str] = None


class IndividualRequestResponse(IndividualRequestBase):
    id: UUID
    status: RequestStatus
    assigned_to: Optional[UUID] = None
    priority: int
    submitted_at: datetime
    acknowledged_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    response_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RequestAssignment(BaseModel):
    assigned_to: UUID
    notes: Optional[str] = None


class RequestStatusUpdate(BaseModel):
    status: RequestStatus
    notes: Optional[str] = None
    response_summary: Optional[str] = None
    response_details: Optional[str] = None


from pydantic import Field
