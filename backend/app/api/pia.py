"""
Privacy Impact Assessment API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.pia import PIAAssessment, PIAStatus
from ..models.adm_system import ADMSystem
from ..schemas.pia import (
    PIAAssessmentCreate,
    PIAAssessmentUpdate,
    PIAAssessmentResponse,
    PIAApprovalRequest
)
from ..services import pdf_generator

router = APIRouter()


@router.post("/start", response_model=PIAAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def start_pia(
    pia_data: PIAAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Start a new Privacy Impact Assessment

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    # Verify ADM system exists
    system = db.query(ADMSystem).filter(ADMSystem.id == pia_data.adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Get next version number
    last_pia = db.query(PIAAssessment).filter(
        PIAAssessment.adm_system_id == pia_data.adm_system_id
    ).order_by(PIAAssessment.version.desc()).first()

    version = (last_pia.version + 1) if last_pia else 1

    # Create PIA
    new_pia = PIAAssessment(
        adm_system_id=pia_data.adm_system_id,
        version=version,
        purpose_description=pia_data.purpose_description,
        necessity_justification=pia_data.necessity_justification,
        purpose_score=pia_data.purpose_score,
        data_minimisation_assessment=pia_data.data_minimisation_assessment,
        data_minimisation_score=pia_data.data_minimisation_score,
        consent_mechanism=pia_data.consent_mechanism,
        notification_method=pia_data.notification_method,
        consent_score=pia_data.consent_score,
        reasonable_expectations_analysis=pia_data.reasonable_expectations_analysis,
        reasonable_expectations_score=pia_data.reasonable_expectations_score,
        sensitive_info_used=pia_data.sensitive_info_used,
        sensitive_info_justification=pia_data.sensitive_info_justification,
        sensitive_info_score=pia_data.sensitive_info_score,
        overall_risk_level=pia_data.overall_risk_level,
        overall_score=pia_data.overall_score,
        recommendations=pia_data.recommendations,
        assessor_id=current_user.id,
        assessment_date=date.today()
    )

    db.add(new_pia)
    db.commit()
    db.refresh(new_pia)

    return new_pia


@router.get("/", response_model=List[PIAAssessmentResponse])
async def list_pias(
    adm_system_id: UUID = None,
    status: PIAStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List Privacy Impact Assessments with optional filters
    """
    query = db.query(PIAAssessment)

    if adm_system_id:
        query = query.filter(PIAAssessment.adm_system_id == adm_system_id)
    if status:
        query = query.filter(PIAAssessment.status == status)

    pias = query.order_by(PIAAssessment.created_at.desc()).all()
    return pias


@router.get("/{pia_id}", response_model=PIAAssessmentResponse)
async def get_pia(
    pia_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific PIA assessment
    """
    pia = db.query(PIAAssessment).filter(PIAAssessment.id == pia_id).first()
    if not pia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PIA assessment not found"
        )

    return pia


@router.put("/{pia_id}", response_model=PIAAssessmentResponse)
async def update_pia(
    pia_id: UUID,
    update_data: PIAAssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Update a PIA assessment

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    pia = db.query(PIAAssessment).filter(PIAAssessment.id == pia_id).first()
    if not pia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PIA assessment not found"
        )

    if pia.status == PIAStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update approved PIA. Create a new version instead."
        )

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(pia, key, value)

    db.commit()
    db.refresh(pia)

    return pia


@router.post("/{pia_id}/approve", response_model=PIAAssessmentResponse)
async def approve_pia(
    pia_id: UUID,
    approval_data: PIAApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer"]))
):
    """
    Approve or reject a PIA assessment

    Requires: Admin or Privacy Officer role
    """
    pia = db.query(PIAAssessment).filter(PIAAssessment.id == pia_id).first()
    if not pia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PIA assessment not found"
        )

    if approval_data.approved:
        pia.status = PIAStatus.APPROVED
        pia.approver_id = current_user.id
        pia.approval_date = date.today()
    else:
        pia.status = PIAStatus.REJECTED
        if approval_data.comments:
            pia.recommendations = approval_data.comments

    db.commit()
    db.refresh(pia)

    return pia


@router.get("/{pia_id}/report")
async def generate_pia_report(
    pia_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PIA report in PDF format
    """
    pia = db.query(PIAAssessment).filter(PIAAssessment.id == pia_id).first()
    if not pia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PIA assessment not found"
        )

    # Get ADM system
    system = db.query(ADMSystem).filter(ADMSystem.id == pia.adm_system_id).first()

    # Generate PDF report
    pdf_content = pdf_generator.generate_pia_report(pia, system)

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=PIA_{pia.id}_{pia.version}.pdf"
        }
    )
