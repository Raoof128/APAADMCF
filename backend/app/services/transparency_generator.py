"""
Transparency & Notification Generator Service
Generates APP5-compliant transparency notices
"""

from typing import Dict, Any
from ..models.adm_system import ADMSystem


def generate_app5_notice(adm_system: ADMSystem) -> Dict[str, str]:
    """
    Generate APP5-compliant transparency notice for an ADM system

    APP5 requires notification about:
    - Identity and contact details of the entity
    - The fact and circumstances of collection
    - If collection is required or authorized by law
    - The purposes of collection
    - The consequences if personal information is not collected
    - The entities to which information is usually disclosed
    - How to access and seek correction
    - How to complain about privacy breaches
    """

    collection_notice = f"""
Personal Information Collection Notice

We collect personal information when you interact with the {adm_system.name} system.

This notice explains how we collect, use, and protect your personal information in accordance
with the Australian Privacy Act 1988 and the Australian Privacy Principles (APPs).

Organisation: [Your Organisation Name]
ABN: [Your ABN]
Contact: privacy@example.gov.au
Phone: 1300 XXX XXX
"""

    purpose_statement = f"""
Purpose of Collection

We collect your personal information for the following purpose:

{adm_system.purpose}

This system uses automated decision-making processes ({adm_system.adm_category.value})
to {adm_system.purpose.lower()}.

The decision impact level is classified as: {adm_system.decision_impact.value}

Legal basis: [Specify the legal authority or individual consent basis]
"""

    data_usage_explanation = f"""
How We Use Your Information

Your personal information is processed through an automated decision-making system that:

1. Collects the minimum necessary information to fulfill the stated purpose
2. Processes this information using {adm_system.model_type or 'automated algorithms'}
3. Makes decisions or recommendations based on predefined criteria
4. Stores your information for {adm_system.data_retention_period or 'the legally required'} days

We implement strict security measures to protect your personal information, including:
- Encryption of data at rest and in transit
- Access controls limiting who can view your information
- Regular security audits and compliance reviews
- Australian data sovereignty (all data stored in Australia)

Your information will not be disclosed to third parties without your consent, except where
required or authorized by law.
"""

    decision_explanation = f"""
Automated Decision-Making

This system makes or assists in making decisions using automated processing. This means:

What happens: Your information is analyzed by computer algorithms that evaluate it against
specific criteria to produce a decision or recommendation.

Decision type: {adm_system.adm_category.value}

Impact level: {adm_system.decision_impact.value} - This decision may have significant effects
on your rights, interests, or access to services.

Factors considered: The system evaluates multiple data points including [list key factors].

The automated decision is {'made entirely by the system' if adm_system.adm_category.value == 'fully_automated' else 'reviewed by human decision-makers before final determination'}.
"""

    rights_explanation = """
Your Privacy Rights

Under the Australian Privacy Act 1988 and the Australian Privacy Principles, you have the right to:

1. Access Your Information (APP 12)
   - Request access to the personal information we hold about you
   - Request a copy of your information in a commonly used format

2. Correction (APP 13)
   - Request correction of inaccurate, out-of-date, incomplete, or misleading information
   - We will notify you of the outcome of your request within 30 days

3. Explanation of Automated Decisions
   - Request an explanation of how an automated decision was made
   - Understand what information was used and how it influenced the outcome

4. Human Review
   - Request human review of an automated decision
   - Have your individual circumstances considered by a qualified person

5. Complain About Privacy Breaches
   - Lodge a complaint if you believe your privacy has been breached
   - Have your complaint investigated and responded to within a reasonable timeframe

6. Withdraw Consent
   - Where we rely on your consent, you may withdraw it at any time
   - This may affect our ability to provide certain services
"""

    review_process_explanation = """
How to Request Review or Explanation

If you wish to:
- Request an explanation of an automated decision
- Seek human review of a decision
- Access or correct your personal information
- Lodge a complaint

Please follow these steps:

1. Submit a Request
   Online: [URL to request portal]
   Email: privacy.requests@example.gov.au
   Mail: Privacy Officer, [Address]
   Phone: 1300 XXX XXX

2. Provide Required Information
   - Your full name and contact details
   - Reference number (if applicable)
   - Description of your request
   - Any supporting documentation

3. We Will Respond
   - Acknowledgment within 5 business days
   - Full response within 30 days
   - If we need more time, we will notify you and explain why

4. If You're Not Satisfied
   - You may escalate to our senior privacy officer
   - You may complain to the Office of the Australian Information Commissioner (OAIC)
     Website: www.oaic.gov.au
     Phone: 1300 363 992

There is no fee for making a request, although we may charge reasonable costs for providing
access to large amounts of information.
"""

    contact_information = """
Contact Us

Privacy Officer
[Organisation Name]
[Street Address]
[City, State, Postcode]

Email: privacy@example.gov.au
Phone: 1300 XXX XXX
Online: www.example.gov.au/privacy

Office Hours: Monday to Friday, 9:00 AM - 5:00 PM AEST

For urgent matters outside business hours, please email urgent.privacy@example.gov.au

This notice was last updated: [Current Date]
Next review date: [Review Date]

For more information about privacy in Australia, visit the Office of the Australian
Information Commissioner at www.oaic.gov.au
"""

    return {
        'collection_notice': collection_notice,
        'purpose_statement': purpose_statement,
        'data_usage_explanation': data_usage_explanation,
        'decision_explanation': decision_explanation,
        'rights_explanation': rights_explanation,
        'review_process_explanation': review_process_explanation,
        'contact_information': contact_information
    }


def generate_machine_readable_metadata(adm_system: ADMSystem) -> Dict[str, Any]:
    """
    Generate machine-readable metadata for ADM system transparency
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': adm_system.name,
        'description': adm_system.description,
        'applicationCategory': 'Automated Decision-Making System',
        'operatingSystem': 'Cloud-based',
        'permissions': 'Processes personal information under Australian Privacy Act 1988',
        'offers': {
            '@type': 'Offer',
            'category': adm_system.adm_category.value,
            'impactLevel': adm_system.decision_impact.value,
        },
        'datePublished': str(adm_system.deployment_date) if adm_system.deployment_date else None,
        'softwareVersion': '1.0',
        'applicationSubCategory': adm_system.model_type,
        'dataRetentionPeriod': f'P{adm_system.data_retention_period}D' if adm_system.data_retention_period else None,
        'privacyPolicy': '[URL to full privacy policy]',
        'termsOfService': '[URL to terms of service]'
    }
