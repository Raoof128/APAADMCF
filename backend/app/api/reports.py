"""
Reports API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime, date

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.report import ComplianceReport
from ..services import report_generator

router = APIRouter()


@router.post("/oaic")
async def generate_oaic_report(
    period_start: date,
    period_end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Generate OAIC-ready ADM Governance Report

    Requires: Admin, Privacy Officer, or Compliance Auditor role

    This report covers:
    - All active ADM systems
    - Privacy Impact Assessments
    - Fairness assessments
    - Individual requests and outcomes
    - Compliance incidents and resolutions
    """
    try:
        report_data = await report_generator.generate_oaic_report(
            db=db,
            period_start=period_start,
            period_end=period_end
        )

        # Generate PDF
        pdf_content = await report_generator.generate_pdf(
            template="oaic_report",
            data=report_data
        )

        # Save report record
        report = ComplianceReport(
            report_type="oaic",
            report_period_start=period_start,
            report_period_end=period_end,
            generated_by=current_user.id,
            file_format="pdf",
            summary=report_data.get("summary", {}),
            metadata={"generated_at": datetime.utcnow().isoformat()}
        )

        db.add(report)
        db.commit()

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=OAIC_ADM_Report_{period_start}_{period_end}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating OAIC report: {str(e)}"
        )


@router.post("/internal")
async def generate_internal_report(
    period_start: date,
    period_end: date,
    include_sensitive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Generate internal risk committee report

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    try:
        report_data = await report_generator.generate_internal_report(
            db=db,
            period_start=period_start,
            period_end=period_end,
            include_sensitive=include_sensitive
        )

        pdf_content = await report_generator.generate_pdf(
            template="internal_report",
            data=report_data
        )

        report = ComplianceReport(
            report_type="internal",
            report_period_start=period_start,
            report_period_end=period_end,
            generated_by=current_user.id,
            file_format="pdf",
            summary=report_data.get("summary", {}),
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "include_sensitive": include_sensitive
            }
        )

        db.add(report)
        db.commit()

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Internal_Report_{period_start}_{period_end}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating internal report: {str(e)}"
        )


@router.post("/fairness-audit/{adm_system_id}")
async def generate_fairness_audit_report(
    adm_system_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "data_scientist", "compliance_auditor"]))
):
    """
    Generate fairness audit report for a specific ADM system

    Requires: Admin, Data Scientist, or Compliance Auditor role
    """
    from ..models.adm_system import ADMSystem

    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    try:
        report_data = await report_generator.generate_fairness_audit(
            db=db,
            adm_system_id=adm_system_id
        )

        pdf_content = await report_generator.generate_pdf(
            template="fairness_audit",
            data=report_data
        )

        report = ComplianceReport(
            report_type="fairness_audit",
            generated_by=current_user.id,
            file_format="pdf",
            summary=report_data.get("summary", {}),
            metadata={
                "adm_system_id": str(adm_system_id),
                "generated_at": datetime.utcnow().isoformat()
            }
        )

        db.add(report)
        db.commit()

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Fairness_Audit_{system.name.replace(' ', '_')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating fairness audit report: {str(e)}"
        )


@router.get("/history")
async def list_reports(
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    List generated reports

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    query = db.query(ComplianceReport)

    if report_type:
        query = query.filter(ComplianceReport.report_type == report_type)

    reports = query.order_by(ComplianceReport.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": query.count(),
        "reports": reports
    }


@router.get("/model-card/{adm_system_id}")
async def generate_model_card(
    adm_system_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate technical model card for an ADM system

    Returns structured metadata about the model for transparency
    """
    from ..models.adm_system import ADMSystem
    from ..models.fairness import FairnessAssessment
    from ..models.pia import PIAAssessment

    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Get latest assessments
    latest_pia = db.query(PIAAssessment).filter(
        PIAAssessment.adm_system_id == adm_system_id
    ).order_by(PIAAssessment.created_at.desc()).first()

    latest_fairness = db.query(FairnessAssessment).filter(
        FairnessAssessment.adm_system_id == adm_system_id
    ).order_by(FairnessAssessment.assessment_date.desc()).first()

    model_card = {
        "model_details": {
            "name": system.name,
            "description": system.description,
            "version": system.metadata.get("version") if system.metadata else "1.0",
            "model_type": system.model_type,
            "deployment_date": str(system.deployment_date) if system.deployment_date else None,
        },
        "intended_use": {
            "purpose": system.purpose,
            "decision_category": system.adm_category.value,
            "impact_level": system.decision_impact.value,
        },
        "performance": {
            "fairness_score": latest_fairness.fairness_score if latest_fairness else None,
            "last_assessed": str(latest_fairness.assessment_date) if latest_fairness else None,
        },
        "privacy_assessment": {
            "pia_status": latest_pia.status.value if latest_pia else "not_assessed",
            "overall_score": latest_pia.overall_score if latest_pia else None,
            "risk_level": latest_pia.overall_risk_level.value if latest_pia and latest_pia.overall_risk_level else None,
        },
        "ethical_considerations": {
            "data_retention_days": system.data_retention_period,
            "last_review": str(system.last_review_date) if system.last_review_date else None,
            "next_review": str(system.next_review_date) if system.next_review_date else None,
        }
    }

    return model_card
