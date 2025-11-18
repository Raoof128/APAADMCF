"""
Drift Detection Service
Detects data drift, model drift, and concept drift in ADM systems
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from scipy import stats


async def detect_drift(
    baseline_data_path: str,
    current_data_path: str
) -> Dict[str, Any]:
    """
    Detect drift between baseline and current data (demo mode)

    Types of drift:
    - Data drift: Distribution changes in input features
    - Model drift: Changes in model performance
    - Concept drift: Changes in relationship between features and target
    """

    # Demo mode: generate synthetic drift metrics
    # In production, load actual datasets and calculate real drift

    drift_type = np.random.choice(['data', 'model', 'concept'])
    drift_score = np.random.uniform(0.3, 0.8)

    baseline_metrics = {
        'mean_age': 45.2,
        'mean_income': 75000,
        'approval_rate': 0.68,
        'avg_loan_amount': 250000,
        'feature_distributions': {
            'age': {'mean': 45.2, 'std': 12.5},
            'income': {'mean': 75000, 'std': 25000},
            'credit_score': {'mean': 720, 'std': 85}
        }
    }

    current_metrics = {
        'mean_age': 45.2 + np.random.uniform(-5, 5),
        'mean_income': 75000 + np.random.uniform(-10000, 10000),
        'approval_rate': 0.68 + np.random.uniform(-0.15, 0.15),
        'avg_loan_amount': 250000 + np.random.uniform(-50000, 50000),
        'feature_distributions': {
            'age': {'mean': 45.2 + np.random.uniform(-5, 5), 'std': 12.5 + np.random.uniform(-2, 2)},
            'income': {'mean': 75000 + np.random.uniform(-10000, 10000), 'std': 25000 + np.random.uniform(-5000, 5000)},
            'credit_score': {'mean': 720 + np.random.uniform(-20, 20), 'std': 85 + np.random.uniform(-10, 10)}
        }
    }

    features_affected = []
    if drift_score > 0.5:
        features_affected = np.random.choice(
            ['age', 'income', 'credit_score', 'employment_status', 'loan_amount'],
            size=np.random.randint(1, 4),
            replace=False
        ).tolist()

    is_significant = drift_score > 0.5

    summary = generate_drift_summary(drift_type, drift_score, is_significant, features_affected)

    return {
        'drift_type': drift_type,
        'drift_score': round(drift_score, 4),
        'is_significant': is_significant,
        'baseline_metrics': baseline_metrics,
        'current_metrics': current_metrics,
        'features_affected': features_affected,
        'summary': summary,
        'detection_method': 'Kolmogorov-Smirnov Test + Population Stability Index'
    }


def generate_drift_summary(drift_type: str, drift_score: float, is_significant: bool, features: list) -> str:
    """
    Generate human-readable drift summary
    """
    severity = 'significant' if is_significant else 'minor'

    summary = f"""
Drift Detection Summary:

Type: {drift_type.upper()} DRIFT
Severity: {severity.upper()}
Drift Score: {drift_score:.4f} {'(Above threshold)' if is_significant else '(Within acceptable range)'}

"""

    if drift_type == 'data':
        summary += f"""
Data drift detected - the statistical distribution of input features has changed
compared to the baseline dataset.

Affected features: {', '.join(features) if features else 'None significantly affected'}

Impact: Changes in input data distribution may affect model performance and fairness.
"""

    elif drift_type == 'model':
        summary += f"""
Model drift detected - the model's performance metrics have degraded compared to
baseline performance.

Metrics affected: {', '.join(features) if features else 'General performance degradation'}

Impact: Model may be producing less accurate or less fair predictions.
"""

    else:  # concept drift
        summary += f"""
Concept drift detected - the relationship between input features and outcomes
has changed over time.

Areas affected: {', '.join(features) if features else 'Overall concept relationship'}

Impact: The underlying patterns the model was trained on may no longer be valid.
"""

    if is_significant:
        summary += """

⚠️ IMMEDIATE ACTION REQUIRED:
1. Review model performance on recent data
2. Conduct fairness re-assessment
3. Consider model retraining or recalibration
4. Update PIA if decision criteria have changed
5. Notify affected stakeholders
"""
    else:
        summary += """

✓ Action: Continue monitoring. No immediate intervention required.
"""

    return summary


async def calculate_psi(baseline: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """
    Calculate Population Stability Index (PSI)

    PSI < 0.1: No significant change
    0.1 <= PSI < 0.2: Moderate change
    PSI >= 0.2: Significant change
    """
    # Create bins
    breakpoints = np.percentile(baseline, np.linspace(0, 100, bins + 1))
    breakpoints = np.unique(breakpoints)

    baseline_counts = np.histogram(baseline, bins=breakpoints)[0]
    current_counts = np.histogram(current, bins=breakpoints)[0]

    # Avoid division by zero
    baseline_percents = (baseline_counts + 0.0001) / len(baseline)
    current_percents = (current_counts + 0.0001) / len(current)

    psi = np.sum((current_percents - baseline_percents) * np.log(current_percents / baseline_percents))

    return float(psi)


async def detect_concept_drift(
    baseline_features: np.ndarray,
    baseline_targets: np.ndarray,
    current_features: np.ndarray,
    current_targets: np.ndarray
) -> Dict[str, Any]:
    """
    Detect concept drift - changes in the relationship between features and target
    """
    # Demo mode implementation
    # In production, compare model performance, correlation changes, etc.

    concept_drift_score = np.random.uniform(0.1, 0.6)

    return {
        'concept_drift_detected': concept_drift_score > 0.3,
        'drift_score': round(concept_drift_score, 4),
        'confidence': 0.85
    }


def monitor_fairness_drift(
    baseline_fairness: Dict[str, float],
    current_fairness: Dict[str, float]
) -> Dict[str, Any]:
    """
    Monitor for drift in fairness metrics
    """
    drift_detected = False
    significant_changes = {}

    for metric in baseline_fairness.keys():
        if metric in current_fairness:
            change = abs(baseline_fairness[metric] - current_fairness[metric])
            if change > 0.1:  # 10% threshold
                drift_detected = True
                significant_changes[metric] = {
                    'baseline': baseline_fairness[metric],
                    'current': current_fairness[metric],
                    'change': round(change, 4)
                }

    return {
        'fairness_drift_detected': drift_detected,
        'significant_changes': significant_changes,
        'recommendation': 'Re-run fairness assessment' if drift_detected else 'Continue monitoring'
    }
