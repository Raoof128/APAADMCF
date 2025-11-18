"""
Individual Requests API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.request import IndividualRequest, RequestHistory, RequestType, RequestStatus
from ..models.adm_system import ADMSystem
from ..schemas.request import (
    IndividualRequestCreate,
    IndividualRequestUpdate,
    IndividualRequestResponse,
    RequestAssignment,
    RequestStatusUpdate
)

router = APIRouter()


@router.post("/", response_model=IndividualRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_request(
    request_data: IndividualRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submit an individual request (public endpoint)

    Types: explanation, human_review, correction, access, deletion, complaint
    """
    # Verify ADM system exists if provided
    if request_data.adm_system_id:
        system = db.query(ADMSystem).filter(ADMSystem.id == request_data.adm_system_id).first()
        if not system:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ADM system not found"
            )

    # Create request
    new_request = IndividualRequest(
        request_type=request_data.request_type,
        requester_name=request_data.requester_name,
        requester_email=request_data.requester_email,
        requester_phone=request_data.requester_phone,
        adm_system_id=request_data.adm_system_id,
        decision_reference=request_data.decision_reference,
        decision_date=request_data.decision_date,
        request_description=request_data.request_description,
        status=RequestStatus.SUBMITTED
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Create history entry
    history = RequestHistory(
        request_id=new_request.id,
        status=RequestStatus.SUBMITTED,
        notes="Request submitted"
    )
    db.add(history)
    db.commit()

    return new_request


@router.get("/", response_model=List[IndividualRequestResponse])
async def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[RequestStatus] = None,
    request_type: Optional[RequestType] = None,
    assigned_to_me: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List individual requests with filters
    """
    query = db.query(IndividualRequest)

    if status:
        query = query.filter(IndividualRequest.status == status)
    if request_type:
        query = query.filter(IndividualRequest.request_type == request_type)
    if assigned_to_me:
        query = query.filter(IndividualRequest.assigned_to == current_user.id)

    requests = query.order_by(IndividualRequest.submitted_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.get("/{request_id}", response_model=IndividualRequestResponse)
async def get_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific request
    """
    request = db.query(IndividualRequest).filter(IndividualRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    return request


@router.post("/{request_id}/assign")
async def assign_request(
    request_id: UUID,
    assignment: RequestAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "individual_request_manager"]))
):
    """
    Assign request to a user

    Requires: Admin, Privacy Officer, or Request Manager role
    """
    request = db.query(IndividualRequest).filter(IndividualRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Verify assignee exists
    assignee = db.query(User).filter(User.id == assignment.assigned_to).first()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    request.assigned_to = assignment.assigned_to
    if request.status == RequestStatus.SUBMITTED:
        request.status = RequestStatus.ACKNOWLEDGED
        request.acknowledged_at = datetime.utcnow()

    # Add history
    history = RequestHistory(
        request_id=request.id,
        status=request.status,
        notes=assignment.notes or f"Assigned to {assignee.full_name}",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    return {"message": "Request assigned successfully"}


@router.put("/{request_id}/status")
async def update_request_status(
    request_id: UUID,
    status_update: RequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "individual_request_manager"]))
):
    """
    Update request status and response

    Requires: Admin, Privacy Officer, or Request Manager role
    """
    request = db.query(IndividualRequest).filter(IndividualRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Update status
    old_status = request.status
    request.status = status_update.status

    if status_update.status == RequestStatus.COMPLETED:
        request.completed_at = datetime.utcnow()

    if status_update.response_summary:
        request.response_summary = status_update.response_summary
    if status_update.response_details:
        request.response_details = status_update.response_details

    # Add history
    history = RequestHistory(
        request_id=request.id,
        status=status_update.status,
        notes=status_update.notes or f"Status changed from {old_status.value} to {status_update.status.value}",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    return {"message": "Request status updated successfully"}


@router.get("/{request_id}/history")
async def get_request_history(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get request history
    """
    request = db.query(IndividualRequest).filter(IndividualRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    history = db.query(RequestHistory).filter(
        RequestHistory.request_id == request_id
    ).order_by(RequestHistory.created_at.asc()).all()

    return history


@router.post("/{request_id}/review")
async def complete_human_review(
    request_id: UUID,
    review_outcome: str,
    review_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer"]))
):
    """
    Complete human review of automated decision

    Requires: Admin or Privacy Officer role
    """
    request = db.query(IndividualRequest).filter(IndividualRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if request.request_type != RequestType.HUMAN_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This is not a human review request"
        )

    request.status = RequestStatus.COMPLETED
    request.completed_at = datetime.utcnow()
    request.response_summary = review_outcome
    request.response_details = review_notes

    # Add history
    history = RequestHistory(
        request_id=request.id,
        status=RequestStatus.COMPLETED,
        notes=f"Human review completed: {review_outcome}",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    return {"message": "Human review completed successfully", "outcome": review_outcome}
