"""
Compliance Monitoring API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.compliance import ComplianceAlert, DriftDetection, AlertSeverity, AlertStatus
from ..models.adm_system import ADMSystem
from ..services import drift_detector

router = APIRouter()


@router.get("/alerts", response_model=List[dict])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
    adm_system_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List compliance alerts with filters
    """
    query = db.query(ComplianceAlert)

    if severity:
        query = query.filter(ComplianceAlert.severity == severity)
    if status:
        query = query.filter(ComplianceAlert.status == status)
    if adm_system_id:
        query = query.filter(ComplianceAlert.adm_system_id == adm_system_id)

    alerts = query.order_by(ComplianceAlert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/alerts/{alert_id}")
async def get_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific alert
    """
    alert = db.query(ComplianceAlert).filter(ComplianceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    return alert


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Acknowledge a compliance alert

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    alert = db.query(ComplianceAlert).filter(ComplianceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    alert.assigned_to = current_user.id

    db.commit()

    return {"message": "Alert acknowledged successfully"}


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "privacy_officer", "compliance_auditor"]))
):
    """
    Resolve a compliance alert

    Requires: Admin, Privacy Officer, or Compliance Auditor role
    """
    alert = db.query(ComplianceAlert).filter(ComplianceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = resolution_notes

    db.commit()

    return {"message": "Alert resolved successfully"}


@router.get("/drift")
async def list_drift_detections(
    adm_system_id: Optional[UUID] = None,
    drift_type: Optional[str] = None,
    significant_only: bool = False,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List drift detections
    """
    query = db.query(DriftDetection)

    # Filter by date range
    since_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(DriftDetection.detection_date >= since_date)

    if adm_system_id:
        query = query.filter(DriftDetection.adm_system_id == adm_system_id)
    if drift_type:
        query = query.filter(DriftDetection.drift_type == drift_type)
    if significant_only:
        query = query.filter(DriftDetection.is_significant == True)

    detections = query.order_by(DriftDetection.detection_date.desc()).all()
    return detections


@router.post("/drift/{adm_system_id}/detect")
async def run_drift_detection(
    adm_system_id: UUID,
    baseline_data_path: str,
    current_data_path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "data_scientist", "privacy_officer"]))
):
    """
    Run drift detection on an ADM system

    Requires: Admin, Data Scientist, or Privacy Officer role
    """
    # Verify ADM system exists
    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    try:
        # Run drift detection (demo mode)
        drift_results = await drift_detector.detect_drift(
            baseline_data_path=baseline_data_path,
            current_data_path=current_data_path
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error detecting drift: {str(e)}"
        )

    # Store drift detection
    detection = DriftDetection(
        adm_system_id=adm_system_id,
        drift_type=drift_results['drift_type'],
        drift_score=drift_results['drift_score'],
        baseline_metrics=drift_results['baseline_metrics'],
        current_metrics=drift_results['current_metrics'],
        features_affected=drift_results.get('features_affected', []),
        is_significant=drift_results['is_significant'],
        notes=drift_results.get('summary', '')
    )

    db.add(detection)

    # Create alert if significant drift detected
    if drift_results['is_significant']:
        alert = ComplianceAlert(
            adm_system_id=adm_system_id,
            alert_type='drift',
            severity=AlertSeverity.WARNING if drift_results['drift_score'] < 0.7 else AlertSeverity.CRITICAL,
            title=f"Significant {drift_results['drift_type']} drift detected",
            description=f"Drift score: {drift_results['drift_score']:.4f}. Immediate review recommended.",
            metrics=drift_results,
            threshold_value=0.5,
            actual_value=float(drift_results['drift_score'])
        )
        db.add(alert)

    db.commit()

    return {
        "detection_id": detection.id,
        "drift_score": drift_results['drift_score'],
        "is_significant": drift_results['is_significant'],
        "alert_created": drift_results['is_significant'],
        "results": drift_results
    }


@router.get("/dashboard")
async def get_compliance_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compliance dashboard metrics
    """
    # Active alerts by severity
    critical_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.severity == AlertSeverity.CRITICAL,
        ComplianceAlert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
    ).count()

    warning_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.severity == AlertSeverity.WARNING,
        ComplianceAlert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
    ).count()

    # Recent drift detections
    recent_drift = db.query(DriftDetection).filter(
        DriftDetection.is_significant == True,
        DriftDetection.detection_date >= datetime.utcnow() - timedelta(days=7)
    ).count()

    # High-risk systems
    from ..models.adm_system import DecisionImpact
    high_risk_systems = db.query(ADMSystem).filter(
        ADMSystem.decision_impact.in_([DecisionImpact.HIGH, DecisionImpact.CRITICAL]),
        ADMSystem.is_active == True
    ).count()

    return {
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "recent_significant_drift": recent_drift,
        "high_risk_systems": high_risk_systems,
        "dashboard_updated_at": datetime.utcnow()
    }
