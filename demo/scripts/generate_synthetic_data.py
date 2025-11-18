"""
Generate synthetic data for ADM compliance framework demo
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

def generate_credit_risk_dataset(n_samples=1000):
    """
    Generate synthetic credit risk assessment dataset
    """
    data = {
        'age': np.random.normal(45, 15, n_samples).clip(18, 85).astype(int),
        'income': np.random.lognormal(11, 0.7, n_samples).clip(20000, 500000).astype(int),
        'employment_years': np.random.exponential(8, n_samples).clip(0, 40).astype(int),
        'credit_score': np.random.normal(720, 85, n_samples).clip(300, 850).astype(int),
        'debt_ratio': np.random.beta(2, 5, n_samples).clip(0, 1),
        'loan_amount': np.random.lognormal(12, 0.6, n_samples).clip(10000, 1000000).astype(int),
        'property_value': np.random.lognormal(13, 0.7, n_samples).clip(100000, 5000000).astype(int),
        'previous_defaults': np.random.binomial(1, 0.15, n_samples),
        'gender': np.random.choice(['M', 'F'], n_samples),
        'region': np.random.choice(['NSW', 'VIC', 'QLD', 'SA', 'WA'], n_samples),
    }

    df = pd.DataFrame(data)

    # Calculate loan-to-value ratio
    df['ltv_ratio'] = df['loan_amount'] / df['property_value']

    # Generate outcome with some bias
    risk_score = (
        - 0.3 * (df['credit_score'] / 850)
        + 0.4 * df['debt_ratio']
        + 0.2 * (df['ltv_ratio'])
        + 0.3 * df['previous_defaults']
        - 0.2 * (df['income'] / 500000)
        + np.random.normal(0, 0.1, n_samples)
    )

    # Introduce slight bias by gender (for fairness testing)
    gender_bias = np.where(df['gender'] == 'F', 0.05, 0)
    risk_score += gender_bias

    # Convert to binary outcome
    threshold = np.percentile(risk_score, 30)  # Approve 70% of applications
    df['approved'] = (risk_score < threshold).astype(int)

    return df


def generate_fraud_detection_dataset(n_samples=5000):
    """
    Generate synthetic fraud detection dataset
    """
    data = {
        'transaction_amount': np.random.lognormal(5, 2, n_samples).clip(1, 50000),
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'merchant_category': np.random.choice(['retail', 'online', 'travel', 'food', 'other'], n_samples),
        'customer_age': np.random.normal(40, 18, n_samples).clip(18, 90).astype(int),
        'account_age_days': np.random.exponential(1000, n_samples).clip(1, 7300).astype(int),
        'previous_transactions': np.random.poisson(50, n_samples),
        'avg_transaction_amount': np.random.lognormal(4, 1.5, n_samples).clip(1, 5000),
        'location_change': np.random.binomial(1, 0.1, n_samples),
        'device_id_change': np.random.binomial(1, 0.05, n_samples),
    }

    df = pd.DataFrame(data)

    # Generate fraud outcome
    fraud_score = (
        0.3 * (df['transaction_amount'] > df['avg_transaction_amount'] * 5)
        + 0.2 * df['location_change']
        + 0.3 * df['device_id_change']
        + 0.1 * (df['hour_of_day'] < 5).astype(int)
        + 0.1 * (df['account_age_days'] < 30).astype(int)
        + np.random.normal(0, 0.2, n_samples)
    )

    threshold = np.percentile(fraud_score, 98)  # 2% fraud rate
    df['is_fraud'] = (fraud_score > threshold).astype(int)

    return df


def generate_hiring_decision_dataset(n_samples=2000):
    """
    Generate synthetic hiring decision dataset
    """
    data = {
        'age': np.random.normal(32, 10, n_samples).clip(20, 65).astype(int),
        'years_experience': np.random.exponential(6, n_samples).clip(0, 40).astype(int),
        'education_level': np.random.choice([1, 2, 3, 4], n_samples, p=[0.2, 0.3, 0.35, 0.15]),
        'technical_score': np.random.normal(75, 15, n_samples).clip(0, 100).astype(int),
        'communication_score': np.random.normal(70, 18, n_samples).clip(0, 100).astype(int),
        'culture_fit_score': np.random.normal(65, 20, n_samples).clip(0, 100).astype(int),
        'previous_companies': np.random.poisson(2, n_samples).clip(0, 10),
        'employment_gap_months': np.random.exponential(3, n_samples).clip(0, 60).astype(int),
        'referral': np.random.binomial(1, 0.25, n_samples),
        'gender': np.random.choice(['M', 'F', 'Other'], n_samples, p=[0.55, 0.43, 0.02]),
        'ethnicity': np.random.choice(['Group_A', 'Group_B', 'Group_C', 'Group_D'], n_samples),
    }

    df = pd.DataFrame(data)

    # Generate hiring outcome with potential bias
    hire_score = (
        0.3 * (df['technical_score'] / 100)
        + 0.2 * (df['communication_score'] / 100)
        + 0.15 * (df['culture_fit_score'] / 100)
        + 0.2 * (df['years_experience'] / 40)
        + 0.1 * (df['education_level'] / 4)
        + 0.05 * df['referral']
        - 0.05 * (df['employment_gap_months'] / 60)
        + np.random.normal(0, 0.15, n_samples)
    )

    # Introduce subtle age bias (for fairness testing)
    age_bias = np.where(df['age'] > 50, -0.08, 0)
    hire_score += age_bias

    threshold = np.percentile(hire_score, 80)  # Hire top 20%
    df['hired'] = (hire_score > threshold).astype(int)

    return df


def main():
    """
    Generate all synthetic datasets
    """
    output_dir = Path(__file__).parent.parent / 'datasets'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic datasets for ADM compliance framework demo...")

    # Credit risk dataset
    print("\n1. Generating credit risk assessment dataset...")
    credit_df = generate_credit_risk_dataset(1000)
    credit_df.to_csv(output_dir / 'credit_risk_baseline.csv', index=False)
    print(f"   Saved {len(credit_df)} records to credit_risk_baseline.csv")
    print(f"   Approval rate: {credit_df['approved'].mean()*100:.1f}%")

    # Generate drift dataset (slightly different distribution)
    print("\n2. Generating credit risk drift dataset...")
    np.random.seed(123)
    credit_drift_df = generate_credit_risk_dataset(1000)
    # Simulate drift by adjusting some distributions
    credit_drift_df['credit_score'] = credit_drift_df['credit_score'] - 10
    credit_drift_df['income'] = credit_drift_df['income'] * 1.15
    credit_drift_df.to_csv(output_dir / 'credit_risk_current.csv', index=False)
    print(f"   Saved {len(credit_drift_df)} records to credit_risk_current.csv")

    # Fraud detection dataset
    print("\n3. Generating fraud detection dataset...")
    fraud_df = generate_fraud_detection_dataset(5000)
    fraud_df.to_csv(output_dir / 'fraud_detection.csv', index=False)
    print(f"   Saved {len(fraud_df)} records to fraud_detection.csv")
    print(f"   Fraud rate: {fraud_df['is_fraud'].mean()*100:.2f}%")

    # Hiring decision dataset
    print("\n4. Generating hiring decision dataset...")
    hiring_df = generate_hiring_decision_dataset(2000)
    hiring_df.to_csv(output_dir / 'hiring_decisions.csv', index=False)
    print(f"   Saved {len(hiring_df)} records to hiring_decisions.csv")
    print(f"   Hiring rate: {hiring_df['hired'].mean()*100:.1f}%")

    # Generate summary statistics
    print("\n" + "="*70)
    print("DATASET SUMMARY")
    print("="*70)

    print("\nCredit Risk Assessment:")
    print(f"  - Total records: {len(credit_df)}")
    print(f"  - Features: {len(credit_df.columns)}")
    print(f"  - Approval rate: {credit_df['approved'].mean()*100:.1f}%")
    print(f"  - Gender distribution: {dict(credit_df['gender'].value_counts())}")

    print("\nFraud Detection:")
    print(f"  - Total records: {len(fraud_df)}")
    print(f"  - Features: {len(fraud_df.columns)}")
    print(f"  - Fraud rate: {fraud_df['is_fraud'].mean()*100:.2f}%")

    print("\nHiring Decisions:")
    print(f"  - Total records: {len(hiring_df)}")
    print(f"  - Features: {len(hiring_df.columns)}")
    print(f"  - Hiring rate: {hiring_df['hired'].mean()*100:.1f}%")
    print(f"  - Gender distribution: {dict(hiring_df['gender'].value_counts())}")

    print("\n" + "="*70)
    print("All datasets generated successfully!")
    print(f"Output directory: {output_dir.absolute()}")
    print("="*70)


if __name__ == "__main__":
    main()
