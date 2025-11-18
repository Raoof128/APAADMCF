"""
PDF Generation Service
Using WeasyPrint for professional PDF reports
"""

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Set up Jinja2 environment
template_dir = Path(__file__).parent.parent / "templates"
template_dir.mkdir(exist_ok=True, parents=True)

env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)


def generate_pia_report(pia, adm_system) -> bytes:
    """
    Generate PIA assessment report PDF
    """
    # Create HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Privacy Impact Assessment Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1 {{
                color: #003366;
                border-bottom: 3px solid #003366;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #005599;
                margin-top: 30px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            .section {{
                margin: 20px 0;
                padding: 15px;
                background-color: #f5f5f5;
                border-left: 4px solid #003366;
            }}
            .score {{
                font-size: 24px;
                font-weight: bold;
                color: #005599;
            }}
            .risk-level {{
                display: inline-block;
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
                background-color: #ffc107;
                color: #000;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #003366;
                color: white;
            }}
            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #ccc;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Privacy Impact Assessment Report</h1>
            <p><strong>ADM System:</strong> {adm_system.name}</p>
            <p><strong>Assessment Version:</strong> {pia.version}</p>
            <p><strong>Status:</strong> {pia.status.value}</p>
            <p><strong>Assessment Date:</strong> {pia.assessment_date or 'N/A'}</p>
        </div>

        <div class="section">
            <h2>Overall Assessment</h2>
            <p><strong>Overall Score:</strong> <span class="score">{pia.overall_score or 'N/A'}/100</span></p>
            <p><strong>Risk Level:</strong> <span class="risk-level">{pia.overall_risk_level.value if pia.overall_risk_level else 'N/A'}</span></p>
        </div>

        <div class="section">
            <h2>Purpose & Necessity Assessment</h2>
            <p><strong>Score:</strong> {pia.purpose_score or 'N/A'}/100</p>
            <p><strong>Purpose Description:</strong></p>
            <p>{pia.purpose_description or 'Not provided'}</p>
            <p><strong>Necessity Justification:</strong></p>
            <p>{pia.necessity_justification or 'Not provided'}</p>
        </div>

        <div class="section">
            <h2>Data Minimisation (APP3 Compliance)</h2>
            <p><strong>Score:</strong> {pia.data_minimisation_score or 'N/A'}/100</p>
            <p>{pia.data_minimisation_assessment or 'Not provided'}</p>
        </div>

        <div class="section">
            <h2>Consent & Notification (APP5 Compliance)</h2>
            <p><strong>Score:</strong> {pia.consent_score or 'N/A'}/100</p>
            <p><strong>Consent Mechanism:</strong> {pia.consent_mechanism or 'Not provided'}</p>
            <p><strong>Notification Method:</strong> {pia.notification_method or 'Not provided'}</p>
        </div>

        <div class="section">
            <h2>Reasonable Expectations Analysis</h2>
            <p><strong>Score:</strong> {pia.reasonable_expectations_score or 'N/A'}/100</p>
            <p>{pia.reasonable_expectations_analysis or 'Not provided'}</p>
        </div>

        <div class="section">
            <h2>Sensitive Information Handling</h2>
            <p><strong>Score:</strong> {pia.sensitive_info_score or 'N/A'}/100</p>
            <p><strong>Sensitive Information Used:</strong> {'Yes' if pia.sensitive_info_used else 'No'}</p>
            <p><strong>Justification:</strong> {pia.sensitive_info_justification or 'Not provided'}</p>
        </div>

        <div class="section">
            <h2>Recommendations</h2>
            <p>{pia.recommendations or 'No specific recommendations'}</p>
        </div>

        <div class="footer">
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Australian Privacy Act ADM Compliance Framework</p>
            <p>This document is confidential and for internal use only.</p>
        </div>
    </body>
    </html>
    """

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()
    return pdf


def generate_transparency_notice_pdf(notice, adm_system) -> bytes:
    """
    Generate transparency notice PDF
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Transparency Notice</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                color: #003366;
                border-bottom: 3px solid #003366;
            }}
            h2 {{
                color: #005599;
                margin-top: 25px;
            }}
            .notice {{
                background-color: #e3f2fd;
                padding: 20px;
                border-left: 5px solid #003366;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <h1>Automated Decision-Making Transparency Notice</h1>
        <p><strong>System:</strong> {adm_system.name}</p>
        <p><strong>Version:</strong> {notice.version}</p>
        <p><strong>Published:</strong> {notice.published_at or 'N/A'}</p>

        <div class="notice">
            <h2>Collection Notice</h2>
            <p>{notice.collection_notice}</p>
        </div>

        <div class="notice">
            <h2>Purpose Statement</h2>
            <p>{notice.purpose_statement}</p>
        </div>

        <div class="notice">
            <h2>How Your Data is Used</h2>
            <p>{notice.data_usage_explanation}</p>
        </div>

        <div class="notice">
            <h2>Automated Decision Explanation</h2>
            <p>{notice.decision_explanation}</p>
        </div>

        <div class="notice">
            <h2>Your Rights</h2>
            <p>{notice.rights_explanation}</p>
        </div>

        <div class="notice">
            <h2>Review Process</h2>
            <p>{notice.review_process_explanation}</p>
        </div>

        <div class="notice">
            <h2>Contact Information</h2>
            <p>{notice.contact_information}</p>
        </div>
    </body>
    </html>
    """

    pdf = HTML(string=html_content).write_pdf()
    return pdf
