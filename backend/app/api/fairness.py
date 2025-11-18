"""
Fairness & Bias Assessment API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user, require_role
from ..models.user import User
from ..models.adm_system import ADMSystem
from ..models.fairness import FairnessAssessment, ExplainabilityResult
from ..services import fairness_analyzer

router = APIRouter()


@router.post("/{adm_system_id}/assess", status_code=status.HTTP_201_CREATED)
async def run_fairness_assessment(
    adm_system_id: UUID,
    dataset_path: str,
    protected_attributes: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "data_scientist", "privacy_officer"]))
):
    """
    Run fairness assessment on an ADM system

    Requires: Admin, Data Scientist, or Privacy Officer role
    """
    # Verify ADM system exists
    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Run fairness analysis (using demo mode for synthetic data)
    try:
        fairness_metrics = await fairness_analyzer.calculate_fairness_metrics(
            dataset_path=dataset_path,
            protected_attributes=protected_attributes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating fairness metrics: {str(e)}"
        )

    # Calculate overall fairness score
    fairness_score = fairness_analyzer.calculate_overall_score(fairness_metrics)

    # Determine if high risk
    is_high_risk = fairness_score < 60

    # Generate recommendations
    recommendations = fairness_analyzer.generate_recommendations(fairness_metrics, is_high_risk)

    # Create fairness assessment
    assessment = FairnessAssessment(
        adm_system_id=adm_system_id,
        dataset_name=dataset_path.split('/')[-1],
        dataset_size=fairness_metrics.get('dataset_size', 0),
        protected_attributes=protected_attributes,
        demographic_parity=fairness_metrics.get('demographic_parity'),
        equal_opportunity=fairness_metrics.get('equal_opportunity'),
        predictive_parity=fairness_metrics.get('predictive_parity'),
        error_rate_ratio=fairness_metrics.get('error_rate_ratio'),
        statistical_parity_difference=fairness_metrics.get('statistical_parity_difference'),
        disparate_impact=fairness_metrics.get('disparate_impact'),
        fairness_score=fairness_score,
        is_high_risk=is_high_risk,
        findings=fairness_metrics.get('summary', ''),
        recommendations=recommendations,
        assessor_id=current_user.id
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "fairness_score": fairness_score,
        "is_high_risk": is_high_risk,
        "metrics": fairness_metrics,
        "recommendations": recommendations
    }


@router.get("/{adm_system_id}/assessments")
async def list_fairness_assessments(
    adm_system_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List fairness assessments for an ADM system
    """
    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    assessments = db.query(FairnessAssessment).filter(
        FairnessAssessment.adm_system_id == adm_system_id
    ).order_by(FairnessAssessment.assessment_date.desc()).all()

    return assessments


@router.post("/{adm_system_id}/explainability")
async def generate_explainability(
    adm_system_id: UUID,
    method: str = "SHAP",
    sample_size: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "data_scientist"]))
):
    """
    Generate explainability analysis (SHAP/LIME)

    Requires: Admin or Data Scientist role
    """
    # Verify ADM system exists
    system = db.query(ADMSystem).filter(ADMSystem.id == adm_system_id).first()
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ADM system not found"
        )

    # Get latest fairness assessment
    latest_assessment = db.query(FairnessAssessment).filter(
        FairnessAssessment.adm_system_id == adm_system_id
    ).order_by(FairnessAssessment.assessment_date.desc()).first()

    if not latest_assessment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fairness assessment found. Run assessment first."
        )

    # Generate explainability (demo mode)
    try:
        explainability_data = await fairness_analyzer.generate_explainability(
            method=method,
            sample_size=sample_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating explainability: {str(e)}"
        )

    # Store results
    result = ExplainabilityResult(
        fairness_assessment_id=latest_assessment.id,
        adm_system_id=adm_system_id,
        method=method,
        feature_importance=explainability_data.get('feature_importance'),
        sample_explanations=explainability_data.get('sample_explanations'),
        visualization_path=explainability_data.get('visualization_path')
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return {
        "result_id": result.id,
        "method": method,
        "feature_importance": explainability_data.get('feature_importance'),
        "visualization_path": explainability_data.get('visualization_path')
    }
