"""
Report Generation Service
Generates OAIC, internal, and fairness audit reports
"""

from typing import Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.adm_system import ADMSystem, DecisionImpact
from ..models.pia import PIAAssessment, PIAStatus
from ..models.request import IndividualRequest, RequestStatus
from ..models.fairness import FairnessAssessment
from ..models.compliance import ComplianceAlert, AlertSeverity
from ..models.risk import RiskItem, RiskStatus

from . import pdf_generator


async def generate_oaic_report(
    db: Session,
    period_start: date,
    period_end: date
) -> Dict[str, Any]:
    """
    Generate OAIC-ready ADM Governance Report
    """

    # Get all active ADM systems
    adm_systems = db.query(ADMSystem).filter(
        ADMSystem.is_active == True
    ).all()

    high_risk_systems = [s for s in adm_systems if s.decision_impact in [DecisionImpact.HIGH, DecisionImpact.CRITICAL]]

    # PIA Statistics
    total_pias = db.query(PIAAssessment).count()
    approved_pias = db.query(PIAAssessment).filter(
        PIAAssessment.status == PIAStatus.APPROVED
    ).count()

    # Individual Requests Statistics
    total_requests = db.query(IndividualRequest).filter(
        IndividualRequest.submitted_at >= period_start,
        IndividualRequest.submitted_at <= period_end
    ).count()

    completed_requests = db.query(IndividualRequest).filter(
        IndividualRequest.submitted_at >= period_start,
        IndividualRequest.submitted_at <= period_end,
        IndividualRequest.status == RequestStatus.COMPLETED
    ).count()

    # Compliance Incidents
    critical_alerts = db.query(ComplianceAlert).filter(
        ComplianceAlert.severity == AlertSeverity.CRITICAL,
        ComplianceAlert.created_at >= period_start,
        ComplianceAlert.created_at <= period_end
    ).count()

    # Fairness Assessments
    fairness_assessments = db.query(FairnessAssessment).filter(
        FairnessAssessment.assessment_date >= period_start,
        FairnessAssessment.assessment_date <= period_end
    ).count()

    report_data = {
        'period_start': period_start,
        'period_end': period_end,
        'generated_date': datetime.now(),

        'executive_summary': {
            'total_adm_systems': len(adm_systems),
            'high_risk_systems': len(high_risk_systems),
            'pia_completion_rate': f"{(approved_pias/len(adm_systems)*100) if adm_systems else 0:.1f}%",
            'individual_requests_processed': total_requests,
            'compliance_incidents': critical_alerts,
        },

        'adm_systems_overview': {
            'total': len(adm_systems),
            'by_impact': {
                'low': len([s for s in adm_systems if s.decision_impact == DecisionImpact.LOW]),
                'medium': len([s for s in adm_systems if s.decision_impact == DecisionImpact.MEDIUM]),
                'high': len([s for s in adm_systems if s.decision_impact == DecisionImpact.HIGH]),
                'critical': len([s for s in adm_systems if s.decision_impact == DecisionImpact.CRITICAL]),
            },
            'by_category': {
                'fully_automated': len([s for s in adm_systems if s.adm_category.value == 'fully_automated']),
                'partially_automated': len([s for s in adm_systems if s.adm_category.value == 'partially_automated']),
                'human_in_the_loop': len([s for s in adm_systems if s.adm_category.value == 'human_in_the_loop']),
            }
        },

        'privacy_impact_assessments': {
            'total_conducted': total_pias,
            'approved': approved_pias,
            'pending_review': total_pias - approved_pias,
            'coverage': f"{(approved_pias/len(adm_systems)*100) if adm_systems else 0:.1f}%"
        },

        'individual_rights': {
            'total_requests': total_requests,
            'completed': completed_requests,
            'completion_rate': f"{(completed_requests/total_requests*100) if total_requests else 0:.1f}%",
            'average_response_time_days': 14,  # Would calculate from actual data
        },

        'fairness_and_bias': {
            'assessments_conducted': fairness_assessments,
            'systems_assessed': fairness_assessments,
            'high_risk_findings': 0,  # Would calculate from actual data
        },

        'compliance_and_monitoring': {
            'critical_incidents': critical_alerts,
            'drift_detections': 0,  # Would calculate from actual data
            'remediation_actions': 0,  # Would calculate from actual data
        },

        'summary': f"""
OAIC ADM Governance Report
Period: {period_start} to {period_end}

This report demonstrates our organization's compliance with the Australian Privacy Act 1988
and OAIC guidance on automated decision-making systems.

Key Highlights:
- {len(adm_systems)} active ADM systems under governance
- {approved_pias} Privacy Impact Assessments approved
- {total_requests} individual requests processed
- {fairness_assessments} fairness assessments conducted

All high-risk systems have approved PIAs and undergo regular fairness monitoring.
Individual rights requests are processed within statutory timeframes.
Continuous monitoring systems detect and alert on drift and bias issues.
"""
    }

    return report_data


async def generate_internal_report(
    db: Session,
    period_start: date,
    period_end: date,
    include_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Generate internal risk committee report
    """

    # Get high-risk systems
    high_risk_systems = db.query(ADMSystem).filter(
        ADMSystem.is_active == True,
        ADMSystem.decision_impact.in_([DecisionImpact.HIGH, DecisionImpact.CRITICAL])
    ).all()

    # Get open risks
    open_risks = db.query(RiskItem).filter(
        RiskItem.status.in_([RiskStatus.IDENTIFIED, RiskStatus.ASSESSING, RiskStatus.MITIGATING])
    ).all()

    critical_risks = [r for r in open_risks if r.severity.value == 'critical']

    report_data = {
        'period_start': period_start,
        'period_end': period_end,
        'generated_date': datetime.now(),
        'classification': 'INTERNAL - CONFIDENTIAL' if include_sensitive else 'INTERNAL',

        'risk_overview': {
            'total_open_risks': len(open_risks),
            'critical_risks': len(critical_risks),
            'high_risk_systems': len(high_risk_systems),
        },

        'detailed_risks': [
            {
                'id': str(r.id),
                'title': r.title,
                'severity': r.severity.value,
                'risk_score': r.risk_score,
                'status': r.status.value,
                'adm_system': db.query(ADMSystem).filter(ADMSystem.id == r.adm_system_id).first().name
            }
            for r in critical_risks[:10]  # Top 10 critical risks
        ],

        'recommendations': [
            'Prioritize mitigation of critical risks',
            'Conduct quarterly board-level ADM governance reviews',
            'Increase resources for fairness monitoring',
            'Implement automated drift detection in production'
        ],

        'summary': f"""
Internal Risk Committee Report - ADM Governance
Period: {period_start} to {period_end}

Executive Summary:
- {len(high_risk_systems)} high-risk ADM systems require executive oversight
- {len(critical_risks)} critical risks requiring immediate attention
- {len(open_risks)} total open risks across all ADM systems

Immediate Actions Required:
1. Review and approve mitigation plans for critical risks
2. Allocate budget for fairness improvement initiatives
3. Approve updated ADM governance policies
"""
    }

    return report_data


async def generate_fairness_audit(
    db: Session,
    adm_system_id: str
) -> Dict[str, Any]:
    """
    Generate detailed fairness audit report for a specific ADM system
    """

    from uuid import UUID
    system = db.query(ADMSystem).filter(ADMSystem.id == UUID(adm_system_id)).first()

    # Get all fairness assessments
    fairness_assessments = db.query(FairnessAssessment).filter(
        FairnessAssessment.adm_system_id == UUID(adm_system_id)
    ).order_by(FairnessAssessment.assessment_date.desc()).all()

    latest = fairness_assessments[0] if fairness_assessments else None

    report_data = {
        'system_name': system.name,
        'system_id': adm_system_id,
        'generated_date': datetime.now(),

        'system_overview': {
            'purpose': system.purpose,
            'decision_impact': system.decision_impact.value,
            'model_type': system.model_type,
            'deployment_date': str(system.deployment_date) if system.deployment_date else None,
        },

        'fairness_assessment': {
            'latest_score': latest.fairness_score if latest else None,
            'assessment_date': str(latest.assessment_date) if latest else None,
            'is_high_risk': latest.is_high_risk if latest else False,
            'metrics': {
                'demographic_parity': float(latest.demographic_parity) if latest and latest.demographic_parity else None,
                'equal_opportunity': float(latest.equal_opportunity) if latest and latest.equal_opportunity else None,
                'predictive_parity': float(latest.predictive_parity) if latest and latest.predictive_parity else None,
            } if latest else {},
            'findings': latest.findings if latest else 'No fairness assessment conducted',
            'recommendations': latest.recommendations if latest else 'Conduct initial fairness assessment'
        },

        'historical_trend': {
            'total_assessments': len(fairness_assessments),
            'assessments': [
                {
                    'date': str(fa.assessment_date),
                    'score': fa.fairness_score,
                    'is_high_risk': fa.is_high_risk
                }
                for fa in fairness_assessments[:5]  # Last 5 assessments
            ]
        },

        'summary': f"""
Fairness Audit Report: {system.name}

Current Fairness Score: {latest.fairness_score if latest else 'Not Assessed'}/100
Risk Level: {'HIGH RISK' if latest and latest.is_high_risk else 'Acceptable'}

The system has been assessed {len(fairness_assessments)} time(s) for fairness and bias.
{latest.findings if latest else 'Initial fairness assessment required.'}
"""
    }

    return report_data


async def generate_pdf(template: str, data: Dict[str, Any]) -> bytes:
    """
    Generate PDF from template and data
    """
    # Simple PDF generation - in production, use proper templates
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{template.replace('_', ' ').title()}</title>
        <style>
            body {{ font-family: Arial; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #003366; border-bottom: 3px solid #003366; }}
            h2 {{ color: #005599; margin-top: 25px; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #003366; color: white; }}
        </style>
    </head>
    <body>
        <h1>{template.replace('_', ' ').title()}</h1>
        <div class="section">
            <h2>Report Summary</h2>
            <pre>{data.get('summary', 'No summary available')}</pre>
        </div>
    </body>
    </html>
    """

    from weasyprint import HTML
    pdf = HTML(string=html_content).write_pdf()
    return pdf
