"""
ADM System Registry API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.adm_system import ADMSystem, ADMCategory, DecisionImpact, SystemStatus
from ..models.pia import PIAAssessment
from ..models.risk import RiskItem
from ..models.request import IndividualRequest
from ..models.fairness import FairnessAssessment
from ..schemas.adm_system import (
    ADMSystemCreate,
    ADMSystemUpdate,
    ADMSystemResponse,
    ADMSystemDetail
)

router = APIRouter()


@router.post("/registry", response_model=ADMSystemResponse, status_code=status.HTTP_201_CREATED)
async def create_adm_system(
    adm_data: ADMSystemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer"]))
):
    """
    Register a new ADM system

    Requires: Admin or Privacy Officer role
    """
    new_system = ADMSystem(
        name=adm_data.name,
        description=adm_data.description,
        owner_id=adm_data.owner_id or current_user.id,
        purpose=adm_data.purpose,
        adm_category=adm_data.adm_category,
        decision_impact=adm_data.decision_impact,
        system_status=adm_data.system_status,
        model_type=adm_data.model_type,
        deployment_date=adm_data.deployment_date,
        data_retention_period=adm_data.data_retention_period,
        metadata=adm_data.metadata,
        created_by=current_user.id
    )

    db.add(new_system)
    db.commit()
    db.refresh(new_system)

    return new_system


@router.get("/registry", response_model=List[ADMSystemResponse])
async def list_adm_systems(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    decision_impact: Optional[DecisionImpact] = None,
    system_status: Optional[SystemStatus] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List ADM systems with optional filters
    """
    query = db.query(ADMSystem)

    if decision_impact:
        query = query.filter(ADMSystem.decision_impact == decision_impact)
    if system_status:
        query = query.filter(ADMSystem.system_status == system_status)
    if is_active is not None:
        query = query.filter(ADMSystem.is_active == is_active)

    systems = query.offset(skip).limit(limit).all()
    return systems


@router.get("/registry/{system_id}", response_model=ADMSystemDetail)
async def get_adm_system(
    system_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about an ADM system
    """
    system = db.query(ADMSystem).filter(ADMSystem.id == system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Get counts
    pia_count = db.query(func.count(PIAAssessment.id)).filter(
        PIAAssessment.adm_system_id == system_id
    ).scalar()

    risk_count = db.query(func.count(RiskItem.id)).filter(
        RiskItem.adm_system_id == system_id,
        RiskItem.status.notin_(["closed", "accepted"])
    ).scalar()

    request_count = db.query(func.count(IndividualRequest.id)).filter(
        IndividualRequest.adm_system_id == system_id,
        IndividualRequest.status.notin_(["completed", "rejected", "withdrawn"])
    ).scalar()

    # Get latest fairness score
    latest_fairness = db.query(FairnessAssessment).filter(
        FairnessAssessment.adm_system_id == system_id
    ).order_by(FairnessAssessment.assessment_date.desc()).first()

    response_dict = {
        **system.__dict__,
        "pia_count": pia_count or 0,
        "risk_count": risk_count or 0,
        "open_request_count": request_count or 0,
        "latest_fairness_score": latest_fairness.fairness_score if latest_fairness else None
    }

    return ADMSystemDetail(**response_dict)


@router.put("/registry/{system_id}", response_model=ADMSystemResponse)
async def update_adm_system(
    system_id: UUID,
    update_data: ADMSystemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer"]))
):
    """
    Update an ADM system

    Requires: Admin or Privacy Officer role
    """
    system = db.query(ADMSystem).filter(ADMSystem.id == system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(system, key, value)

    system.updated_by = current_user.id

    db.commit()
    db.refresh(system)

    return system


@router.delete("/registry/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adm_system(
    system_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Delete an ADM system (soft delete)

    Requires: Admin role
    """
    system = db.query(ADMSystem).filter(ADMSystem.id == system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Soft delete
    system.is_active = False
    system.system_status = SystemStatus.DECOMMISSIONED
    system.updated_by = current_user.id

    db.commit()

    return None
