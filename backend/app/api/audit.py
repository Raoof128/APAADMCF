"""
Audit & Governance API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.audit import AuditLog, AuditAction

router = APIRouter()


@router.get("/logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[UUID] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "compliance_auditor"]))
):
    """
    Get audit logs with filters

    Requires: Admin or Compliance Auditor role

    Note: Audit logs are immutable and cannot be modified or deleted
    """
    query = db.query(AuditLog)

    # Filter by date range
    since_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(AuditLog.created_at >= since_date)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)

    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": query.count(),
        "logs": logs
    }


@router.get("/logs/export")
async def export_audit_logs(
    start_date: datetime,
    end_date: datetime,
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "compliance_auditor"]))
):
    """
    Export audit logs for a date range

    Requires: Admin or Compliance Auditor role

    Formats: json, csv
    """
    logs = db.query(AuditLog).filter(
        AuditLog.created_at >= start_date,
        AuditLog.created_at <= end_date
    ).order_by(AuditLog.created_at.asc()).all()

    if format == "json":
        return {
            "export_date": datetime.utcnow(),
            "period_start": start_date,
            "period_end": end_date,
            "total_logs": len(logs),
            "logs": logs
        }
    else:
        # CSV format would be implemented here
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="CSV export not yet implemented"
        )


@router.get("/activity/user/{user_id}")
async def get_user_activity(
    user_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "compliance_auditor"]))
):
    """
    Get activity summary for a specific user

    Requires: Admin or Compliance Auditor role
    """
    since_date = datetime.utcnow() - timedelta(days=days)

    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.created_at >= since_date
    ).all()

    # Group by action
    from collections import Counter
    action_counts = Counter([log.action.value for log in logs])

    # Group by resource type
    resource_counts = Counter([log.resource_type for log in logs if log.resource_type])

    return {
        "user_id": user_id,
        "period_days": days,
        "total_actions": len(logs),
        "actions_by_type": dict(action_counts),
        "resources_accessed": dict(resource_counts),
        "last_activity": max([log.created_at for log in logs]) if logs else None
    }


@router.get("/activity/resource/{resource_type}/{resource_id}")
async def get_resource_activity(
    resource_type: str,
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "compliance_auditor"]))
):
    """
    Get activity history for a specific resource

    Requires: Admin or Compliance Auditor role
    """
    logs = db.query(AuditLog).filter(
        AuditLog.resource_type == resource_type,
        AuditLog.resource_id == resource_id
    ).order_by(AuditLog.created_at.desc()).all()

    return {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "total_events": len(logs),
        "events": logs
    }


@router.get("/compliance/summary")
async def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Get overall compliance summary

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    from ..models.adm_system import ADMSystem
    from ..models.pia import PIAAssessment, PIAStatus
    from ..models.request import IndividualRequest, RequestStatus
    from ..models.compliance import ComplianceAlert, AlertStatus, AlertSeverity

    # ADM Systems
    total_systems = db.query(ADMSystem).filter(ADMSystem.is_active == True).count()

    # PIAs
    approved_pias = db.query(PIAAssessment).filter(PIAAssessment.status == PIAStatus.APPROVED).count()
    pending_pias = db.query(PIAAssessment).filter(
        PIAAssessment.status.in_([PIAStatus.DRAFT, PIAStatus.IN_REVIEW])
    ).count()

    # Individual Requests
    open_requests = db.query(IndividualRequest).filter(
        IndividualRequest.status.in_([
            RequestStatus.SUBMITTED,
            RequestStatus.ACKNOWLEDGED,
            RequestStatus.IN_PROGRESS
        ])
    ).count()

    overdue_requests = db.query(IndividualRequest).filter(
        IndividualRequest.status.in_([
            RequestStatus.SUBMITTED,
            RequestStatus.ACKNOWLEDGED,
            RequestStatus.IN_PROGRESS
        ]),
        IndividualRequest.due_date < datetime.utcnow()
    ).count()

    # Alerts
    active_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
    ).count()

    critical_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.severity == AlertSeverity.CRITICAL,
        ComplianceAlert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
    ).count()

    return {
        "summary_date": datetime.utcnow(),
        "adm_systems": {
            "total_active": total_systems
        },
        "pia_assessments": {
            "approved": approved_pias,
            "pending": pending_pias
        },
        "individual_requests": {
            "open": open_requests,
            "overdue": overdue_requests
        },
        "compliance_alerts": {
            "active": active_alerts,
            "critical": critical_alerts
        }
    }
