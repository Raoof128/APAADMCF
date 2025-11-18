"""
Transparency & Notification API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.adm_system import ADMSystem
from ..models.transparency import TransparencyNotice
from ..services import transparency_generator

router = APIRouter()


@router.post("/notice", status_code=status.HTTP_201_CREATED)
async def generate_transparency_notice(
    adm_system_id: UUID,
    language: str = "en",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer"]))
):
    """
    Generate APP5-compliant transparency notice for an ADM system

    Requires: Admin or Privacy Officer role
    """
    # Verify ADM system exists
    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Generate notice content
    notice_content = transparency_generator.generate_app5_notice(system)

    # Get next version
    last_notice = db.query(TransparencyNotice).filter(
        TransparencyNotice.adm_system_id == adm_system_id
    ).order_by(TransparencyNotice.version.desc()).first()

    version = (last_notice.version + 1) if last_notice else 1

    # Deactivate previous notices
    if last_notice:
        db.query(TransparencyNotice).filter(
            TransparencyNotice.adm_system_id == adm_system_id,
            TransparencyNotice.is_active == True
        ).update({"is_active": False})

    # Create new notice
    notice = TransparencyNotice(
        adm_system_id=adm_system_id,
        version=version,
        collection_notice=notice_content['collection_notice'],
        purpose_statement=notice_content['purpose_statement'],
        data_usage_explanation=notice_content['data_usage_explanation'],
        decision_explanation=notice_content['decision_explanation'],
        rights_explanation=notice_content['rights_explanation'],
        review_process_explanation=notice_content['review_process_explanation'],
        contact_information=notice_content['contact_information'],
        language=language,
        is_active=True,
        published_at=datetime.utcnow(),
        created_by=current_user.id
    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    return {
        "notice_id": notice.id,
        "version": version,
        "content": notice_content,
        "published_at": notice.published_at
    }


@router.get("/notice/{adm_system_id}")
async def get_active_notice(
    adm_system_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get active transparency notice for an ADM system

    Public endpoint - no authentication required
    """
    notice = db.query(TransparencyNotice).filter(
        TransparencyNotice.adm_system_id == adm_system_id,
        TransparencyNotice.is_active == True
    ).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active transparency notice found for this system"
        )

    return {
        "system_id": notice.adm_system_id,
        "version": notice.version,
        "collection_notice": notice.collection_notice,
        "purpose_statement": notice.purpose_statement,
        "data_usage_explanation": notice.data_usage_explanation,
        "decision_explanation": notice.decision_explanation,
        "rights_explanation": notice.rights_explanation,
        "review_process_explanation": notice.review_process_explanation,
        "contact_information": notice.contact_information,
        "published_at": notice.published_at
    }


@router.get("/notice/{adm_system_id}/metadata")
async def get_adm_metadata(
    adm_system_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get machine-readable ADM metadata (JSON)

    Public endpoint - no authentication required
    """
    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    metadata = {
        "system_id": str(system.id),
        "system_name": system.name,
        "purpose": system.purpose,
        "adm_category": system.adm_category.value,
        "decision_impact": system.decision_impact.value,
        "model_type": system.model_type,
        "deployment_date": str(system.deployment_date) if system.deployment_date else None,
        "last_review_date": str(system.last_review_date) if system.last_review_date else None,
        "data_retention_period_days": system.data_retention_period,
        "metadata": system.metadata or {}
    }

    return metadata
