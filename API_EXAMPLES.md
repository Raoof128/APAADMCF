# API Examples and Usage Guide

**Australian Privacy Act ADM Compliance Framework**

Version: 1.0.0
Last Updated: 2024-01-XX

---

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [ADM System Registry](#adm-system-registry)
- [Privacy Impact Assessments](#privacy-impact-assessments)
- [Fairness Assessments](#fairness-assessments)
- [Individual Rights Requests](#individual-rights-requests)
- [Compliance Monitoring](#compliance-monitoring)
- [Reports and Exports](#reports-and-exports)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Webhooks](#webhooks)

---

## Getting Started

### Base URLs

| Environment | Base URL |
|-------------|----------|
| **Local Development** | `http://localhost:8000/api` |
| **Staging** | `https://api.staging.adm-compliance.gov.au/api` |
| **Production** | `https://api.adm-compliance.gov.au/api` |

### API Documentation

- **Interactive Docs**: `{BASE_URL}/docs` (Swagger UI)
- **OpenAPI Spec**: `{BASE_URL}/openapi.json`
- **ReDoc**: `{BASE_URL}/redoc`

### Common Headers

```http
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
Accept: application/json
```

---

## Authentication

### 1. User Registration

**Endpoint:** `POST /auth/register`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "privacy.officer@example.gov.au",
    "password": "SecurePassword123!",
    "full_name": "Jane Smith",
    "role": "privacy_officer",
    "organization": "Example Government Department"
  }'
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "privacy.officer@example.gov.au",
  "full_name": "Jane Smith",
  "role": "privacy_officer",
  "organization": "Example Government Department",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. User Login

**Endpoint:** `POST /auth/login`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "privacy.officer@example.gov.au",
    "password": "SecurePassword123!"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "privacy.officer@example.gov.au",
    "full_name": "Jane Smith",
    "role": "privacy_officer"
  }
}
```

**Save the token for subsequent requests:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Refresh Token

**Endpoint:** `POST /auth/refresh`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. Get Current User

**Endpoint:** `GET /auth/me`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "privacy.officer@example.gov.au",
  "full_name": "Jane Smith",
  "role": "privacy_officer",
  "organization": "Example Government Department",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-16T09:15:00Z"
}
```

---

## ADM System Registry

### 1. Create ADM System

**Endpoint:** `POST /adm-systems`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/adm-systems" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welfare Payment Eligibility System",
    "description": "Automated system for determining eligibility for welfare payments based on income, assets, and household composition.",
    "business_unit": "Department of Social Services",
    "decision_type": "eligibility",
    "impact_level": "high",
    "deployment_status": "production",
    "affected_population_size": 2500000,
    "decisions_per_month": 150000,
    "technology_stack": "Python ML model (Random Forest), deployed on Azure ML",
    "data_sources": ["Centrelink database", "ATO income data", "MyGov submissions"],
    "decision_criteria": ["Income thresholds", "Asset tests", "Residency status", "Age verification"],
    "review_mechanism": "Human review available on request within 28 days",
    "appeals_process": "Administrative Appeals Tribunal (AAT) review available",
    "contact_email": "welfare.systems@dss.gov.au",
    "contact_phone": "+61 2 6244 7788"
  }'
```

**Response (201 Created):**
```json
{
  "id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "name": "Welfare Payment Eligibility System",
  "description": "Automated system for determining eligibility...",
  "business_unit": "Department of Social Services",
  "decision_type": "eligibility",
  "impact_level": "high",
  "deployment_status": "production",
  "affected_population_size": 2500000,
  "decisions_per_month": 150000,
  "compliance_status": "pending_assessment",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "technology_stack": "Python ML model (Random Forest), deployed on Azure ML",
    "data_sources": ["Centrelink database", "ATO income data"],
    "decision_criteria": ["Income thresholds", "Asset tests"],
    "review_mechanism": "Human review available on request within 28 days",
    "appeals_process": "Administrative Appeals Tribunal (AAT) review available"
  }
}
```

### 2. List ADM Systems

**Endpoint:** `GET /adm-systems`

**Query Parameters:**
- `skip` (int): Number of records to skip (pagination)
- `limit` (int): Maximum records to return (default: 50, max: 100)
- `decision_type` (string): Filter by decision type
- `impact_level` (string): Filter by impact level
- `compliance_status` (string): Filter by compliance status

**Request:**
```bash
curl -X GET "http://localhost:8000/api/adm-systems?impact_level=high&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
      "name": "Welfare Payment Eligibility System",
      "business_unit": "Department of Social Services",
      "decision_type": "eligibility",
      "impact_level": "high",
      "compliance_status": "compliant",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### 3. Get ADM System Details

**Endpoint:** `GET /adm-systems/{id}`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/adm-systems/adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "name": "Welfare Payment Eligibility System",
  "description": "Automated system for determining eligibility...",
  "business_unit": "Department of Social Services",
  "decision_type": "eligibility",
  "impact_level": "high",
  "deployment_status": "production",
  "compliance_status": "compliant",
  "last_pia_date": "2024-01-10T00:00:00Z",
  "last_fairness_assessment_date": "2024-01-12T00:00:00Z",
  "pias": [
    {
      "id": "pia_1a2b3c4d",
      "status": "completed",
      "completed_at": "2024-01-10T15:30:00Z",
      "overall_risk_level": "medium"
    }
  ],
  "fairness_assessments": [
    {
      "id": "fa_5e6f7g8h",
      "assessed_at": "2024-01-12T10:00:00Z",
      "overall_fairness_score": 0.87
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. Update ADM System

**Endpoint:** `PUT /adm-systems/{id}`

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/adm-systems/adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "deployment_status": "production",
    "decisions_per_month": 175000
  }'
```

**Response (200 OK):**
```json
{
  "id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "name": "Welfare Payment Eligibility System",
  "deployment_status": "production",
  "decisions_per_month": 175000,
  "updated_at": "2024-01-16T11:20:00Z"
}
```

### 5. Delete ADM System

**Endpoint:** `DELETE /adm-systems/{id}`

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/adm-systems/adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (204 No Content)**

---

## Privacy Impact Assessments

### 1. Create PIA

**Endpoint:** `POST /pias`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/pias" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
    "assessor_name": "Jane Smith",
    "assessor_email": "jane.smith@example.gov.au",
    "assessment_scope": "Full system assessment including data flows, security controls, and individual rights implementation",
    "data_collected": [
      "Full name",
      "Date of birth",
      "Tax File Number",
      "Income records",
      "Bank account details",
      "Residential address",
      "Family composition"
    ],
    "legal_basis": "Social Security Act 1991 - Section 192",
    "data_retention_period_days": 2555,
    "third_party_sharing": true,
    "third_parties": ["Australian Taxation Office", "Department of Home Affairs"],
    "international_transfers": false
  }'
```

**Response (201 Created):**
```json
{
  "id": "pia_1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "status": "draft",
  "assessor_name": "Jane Smith",
  "assessor_email": "jane.smith@example.gov.au",
  "created_at": "2024-01-15T10:30:00Z",
  "overall_risk_level": null,
  "pdf_report_url": null
}
```

### 2. Complete PIA Assessment

**Endpoint:** `PUT /pias/{id}/complete`

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/pias/pia_1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "risk_assessments": [
      {
        "risk_category": "Unauthorized Access",
        "severity": "high",
        "likelihood": 0.3,
        "impact_score": 0.9,
        "description": "Potential for unauthorized access to sensitive welfare data",
        "existing_controls": "Multi-factor authentication, role-based access control, audit logging",
        "residual_risk": "medium"
      },
      {
        "risk_category": "Data Breach",
        "severity": "critical",
        "likelihood": 0.1,
        "impact_score": 1.0,
        "description": "Exposure of personal information through security breach",
        "existing_controls": "Encryption at rest and in transit, network segmentation, DLP controls",
        "residual_risk": "low"
      },
      {
        "risk_category": "Algorithmic Bias",
        "severity": "high",
        "likelihood": 0.4,
        "impact_score": 0.8,
        "description": "Potential for discriminatory outcomes against protected groups",
        "existing_controls": "Fairness testing, diverse training data, human oversight",
        "residual_risk": "medium"
      }
    ],
    "mitigation_actions": [
      {
        "action": "Implement quarterly fairness audits",
        "priority": "high",
        "responsible_party": "Data Science Team",
        "due_date": "2024-03-31",
        "status": "planned"
      },
      {
        "action": "Enhanced access logging and monitoring",
        "priority": "medium",
        "responsible_party": "Security Team",
        "due_date": "2024-02-28",
        "status": "in_progress"
      }
    ],
    "recommendations": "1. Conduct annual PIA reviews\n2. Implement real-time bias monitoring\n3. Provide transparency notices to all affected individuals"
  }'
```

**Response (200 OK):**
```json
{
  "id": "pia_1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "status": "completed",
  "overall_risk_level": "medium",
  "completed_at": "2024-01-15T14:30:00Z",
  "pdf_report_url": "https://admcomplianceprod.blob.core.windows.net/reports/pia_1a2b3c4d_report.pdf"
}
```

### 3. Download PIA Report

**Endpoint:** `GET /pias/{id}/report`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/pias/pia_1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p/report" \
  -H "Authorization: Bearer $TOKEN" \
  -o pia_report.pdf
```

**Response:** PDF file download

---

## Fairness Assessments

### 1. Create Fairness Assessment

**Endpoint:** `POST /fairness/assessments`

**Request (with CSV upload):**
```bash
curl -X POST "http://localhost:8000/api/fairness/assessments" \
  -H "Authorization: Bearer $TOKEN" \
  -F "adm_system_id=adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d" \
  -F "protected_attributes=gender,age_group,indigenous_status" \
  -F "outcome_column=approved" \
  -F "dataset=@predictions.csv"
```

**Predictions.csv format:**
```csv
id,gender,age_group,indigenous_status,approved,prediction_score
1,male,25-34,no,1,0.87
2,female,35-44,no,1,0.92
3,male,45-54,yes,0,0.42
4,female,25-34,no,1,0.88
```

**Alternative: JSON payload with inline data:**
```bash
curl -X POST "http://localhost:8000/api/fairness/assessments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
    "protected_attributes": ["gender", "age_group", "indigenous_status"],
    "outcome_column": "approved",
    "dataset": {
      "records": [
        {"gender": "male", "age_group": "25-34", "indigenous_status": "no", "approved": 1, "score": 0.87},
        {"gender": "female", "age_group": "35-44", "indigenous_status": "no", "approved": 1, "score": 0.92}
      ]
    }
  }'
```

**Response (201 Created):**
```json
{
  "id": "fa_5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "assessed_at": "2024-01-16T10:00:00Z",
  "overall_fairness_score": 0.72,
  "bias_detected": true,
  "dataset_stats": {
    "total_records": 10000,
    "positive_outcomes": 6500,
    "negative_outcomes": 3500,
    "protected_groups": {
      "gender": {"male": 4800, "female": 5200},
      "age_group": {"18-24": 1500, "25-34": 3000, "35-44": 2500, "45-54": 2000, "55+": 1000},
      "indigenous_status": {"yes": 800, "no": 9200}
    }
  },
  "metrics": [
    {
      "metric_name": "demographic_parity",
      "protected_attribute": "gender",
      "reference_group": "male",
      "comparison_group": "female",
      "metric_value": 0.15,
      "threshold": 0.1,
      "passes_threshold": false,
      "interpretation": "Female applicants approved 15% less often than male applicants"
    },
    {
      "metric_name": "equal_opportunity",
      "protected_attribute": "indigenous_status",
      "reference_group": "no",
      "comparison_group": "yes",
      "metric_value": 0.22,
      "threshold": 0.1,
      "passes_threshold": false,
      "interpretation": "Indigenous applicants have 22% lower true positive rate"
    }
  ],
  "recommendations": [
    "Review model training data for gender representation",
    "Investigate features correlated with indigenous status",
    "Consider implementing fairness constraints in model training",
    "Conduct qualitative review of denied cases for indigenous applicants"
  ]
}
```

### 2. Get Fairness Assessment Details

**Endpoint:** `GET /fairness/assessments/{id}`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/fairness/assessments/fa_5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "id": "fa_5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "assessed_at": "2024-01-16T10:00:00Z",
  "overall_fairness_score": 0.72,
  "bias_detected": true,
  "metrics": [...],
  "detailed_analysis": {
    "confusion_matrices": {
      "gender": {
        "male": {"TP": 3200, "FP": 400, "TN": 800, "FN": 400},
        "female": {"TP": 3100, "FP": 500, "TN": 1200, "FN": 400}
      }
    },
    "statistical_tests": {
      "chi_square_test": {
        "statistic": 12.45,
        "p_value": 0.002,
        "significant": true
      }
    }
  }
}
```

### 3. List Fairness Metrics

**Endpoint:** `GET /fairness/assessments/{id}/metrics`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/fairness/assessments/fa_5e6f7g8h/metrics?protected_attribute=gender" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "assessment_id": "fa_5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t",
  "protected_attribute": "gender",
  "metrics": [
    {
      "metric_name": "demographic_parity",
      "metric_value": 0.15,
      "passes_threshold": false,
      "details": {
        "male_approval_rate": 0.75,
        "female_approval_rate": 0.60,
        "disparity": 0.15
      }
    },
    {
      "metric_name": "equal_opportunity",
      "metric_value": 0.08,
      "passes_threshold": true,
      "details": {
        "male_tpr": 0.89,
        "female_tpr": 0.81,
        "disparity": 0.08
      }
    },
    {
      "metric_name": "predictive_parity",
      "metric_value": 0.12,
      "passes_threshold": false,
      "details": {
        "male_ppv": 0.88,
        "female_ppv": 0.76,
        "disparity": 0.12
      }
    }
  ]
}
```

---

## Individual Rights Requests

### 1. Submit Access Request

**Endpoint:** `POST /requests`

**Request (Public endpoint - no auth required):**
```bash
curl -X POST "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "access",
    "individual_name": "John Citizen",
    "individual_email": "john.citizen@email.com",
    "individual_phone": "+61 400 123 456",
    "date_of_birth": "1985-03-15",
    "identification_provided": "Drivers License: VIC123456",
    "details": "I request access to all personal information held about me in the Welfare Payment Eligibility System, including decision records and assessment data.",
    "preferred_format": "pdf",
    "consent_to_verification": true
  }'
```

**Response (202 Accepted):**
```json
{
  "id": "req_9u8v7w6x-5y4z-3a2b-1c0d-9e8f7g6h5i4j",
  "request_type": "access",
  "tracking_id": "ADM-2024-00123",
  "status": "pending_verification",
  "submitted_at": "2024-01-16T11:00:00Z",
  "due_date": "2024-02-15T23:59:59Z",
  "verification_instructions": "A verification email has been sent to john.citizen@email.com. Please click the link to verify your identity.",
  "estimated_response_time_days": 30
}
```

### 2. Verify Request

**Endpoint:** `GET /requests/{id}/verify?token={verification_token}`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/requests/req_9u8v7w6x/verify?token=abc123xyz456" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "id": "req_9u8v7w6x-5y4z-3a2b-1c0d-9e8f7g6h5i4j",
  "tracking_id": "ADM-2024-00123",
  "status": "verified",
  "verified_at": "2024-01-16T11:15:00Z",
  "message": "Your request has been verified and is now being processed. You will receive an email when a response is available."
}
```

### 3. Track Request Status

**Endpoint:** `GET /requests/{tracking_id}`

**Request (Public endpoint):**
```bash
curl -X GET "http://localhost:8000/api/requests/ADM-2024-00123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "tracking_id": "ADM-2024-00123",
  "status": "in_progress",
  "submitted_at": "2024-01-16T11:00:00Z",
  "verified_at": "2024-01-16T11:15:00Z",
  "due_date": "2024-02-15T23:59:59Z",
  "progress": {
    "current_step": "Data retrieval in progress",
    "steps_completed": ["Verification", "Request assignment"],
    "steps_remaining": ["Data retrieval", "Review", "Response preparation"]
  },
  "estimated_completion": "2024-02-10T00:00:00Z"
}
```

### 4. Privacy Officer: List Requests

**Endpoint:** `GET /requests` (Authenticated)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/requests?status=verified&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "req_9u8v7w6x-5y4z-3a2b-1c0d-9e8f7g6h5i4j",
      "tracking_id": "ADM-2024-00123",
      "request_type": "access",
      "individual_name": "John Citizen",
      "status": "verified",
      "submitted_at": "2024-01-16T11:00:00Z",
      "due_date": "2024-02-15T23:59:59Z",
      "assigned_to": null,
      "priority": "normal"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 20
}
```

### 5. Privacy Officer: Respond to Request

**Endpoint:** `POST /requests/{id}/response`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/requests/req_9u8v7w6x/response" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_type": "approved",
    "response_text": "Please find attached your personal information as requested. This includes all records from the Welfare Payment Eligibility System from 2020-2024.",
    "documents": [
      {
        "filename": "personal_data_export.pdf",
        "file_url": "https://secure.adm-compliance.gov.au/downloads/abc123"
      }
    ],
    "notes": "Data exported on 2024-01-20, includes 15 decision records"
  }'
```

**Response (200 OK):**
```json
{
  "id": "req_9u8v7w6x-5y4z-3a2b-1c0d-9e8f7g6h5i4j",
  "status": "completed",
  "response_provided_at": "2024-01-20T14:30:00Z",
  "response_type": "approved",
  "notification_sent": true
}
```

---

## Compliance Monitoring

### 1. Get Compliance Dashboard

**Endpoint:** `GET /compliance/dashboard`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/compliance/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "overview": {
    "total_adm_systems": 47,
    "compliant_systems": 38,
    "non_compliant_systems": 6,
    "pending_assessment": 3,
    "compliance_rate": 0.809
  },
  "by_impact_level": {
    "critical": {"total": 8, "compliant": 6, "rate": 0.75},
    "high": {"total": 15, "compliant": 13, "rate": 0.867},
    "medium": {"total": 18, "compliant": 15, "rate": 0.833},
    "low": {"total": 6, "compliant": 4, "rate": 0.667}
  },
  "recent_pias": [
    {
      "id": "pia_1a2b3c4d",
      "adm_system_name": "Welfare Payment Eligibility System",
      "completed_at": "2024-01-10T00:00:00Z",
      "overall_risk_level": "medium"
    }
  ],
  "pending_actions": {
    "overdue_pias": 2,
    "overdue_fairness_assessments": 1,
    "high_risk_systems": 3,
    "pending_requests": 12
  },
  "trends": {
    "pia_completion_rate_30d": 0.92,
    "average_request_response_time_days": 18.5,
    "bias_detection_rate": 0.15
  }
}
```

### 2. Run Compliance Check

**Endpoint:** `POST /compliance/checks`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/compliance/checks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
    "check_types": ["pia_current", "fairness_assessed", "transparency_notice", "individual_rights"]
  }'
```

**Response (200 OK):**
```json
{
  "id": "check_3b4c5d6e-7f8g-9h0i-1j2k-3l4m5n6o7p8q",
  "adm_system_id": "adm_7d3f8a2b-4c1e-4a8f-9b2d-1e6c8f3a5b7d",
  "checked_at": "2024-01-16T12:00:00Z",
  "overall_result": "non_compliant",
  "checks": [
    {
      "check_type": "pia_current",
      "result": "pass",
      "details": "PIA completed on 2024-01-10 (within 12 months)"
    },
    {
      "check_type": "fairness_assessed",
      "result": "pass",
      "details": "Fairness assessment completed on 2024-01-12 (within 6 months)"
    },
    {
      "check_type": "transparency_notice",
      "result": "fail",
      "details": "No transparency notice generated for this system",
      "remediation": "Generate and publish transparency notice"
    },
    {
      "check_type": "individual_rights",
      "result": "pass",
      "details": "Request handling process documented and operational"
    }
  ],
  "recommendations": [
    "Generate transparency notice immediately",
    "Publish transparency notice on public website",
    "Schedule next PIA for 2025-01-10"
  ]
}
```

---

## Reports and Exports

### 1. Generate Compliance Report

**Endpoint:** `POST /reports/compliance`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/reports/compliance" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_period_start": "2024-01-01",
    "report_period_end": "2024-01-31",
    "include_sections": ["executive_summary", "system_inventory", "pia_summary", "fairness_results", "individual_requests"],
    "format": "pdf"
  }'
```

**Response (202 Accepted):**
```json
{
  "task_id": "task_7h8i9j0k-1l2m-3n4o-5p6q-7r8s9t0u1v2w",
  "status": "processing",
  "estimated_completion": "2024-01-16T12:10:00Z",
  "message": "Report generation in progress. You will receive an email when ready."
}
```

### 2. Check Report Status

**Endpoint:** `GET /reports/tasks/{task_id}`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/reports/tasks/task_7h8i9j0k" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "task_id": "task_7h8i9j0k-1l2m-3n4o-5p6q-7r8s9t0u1v2w",
  "status": "completed",
  "created_at": "2024-01-16T12:00:00Z",
  "completed_at": "2024-01-16T12:08:00Z",
  "report_url": "https://admcomplianceprod.blob.core.windows.net/reports/compliance_2024-01.pdf",
  "expires_at": "2024-01-23T12:08:00Z"
}
```

### 3. Export ADM Systems (CSV)

**Endpoint:** `GET /adm-systems/export`

**Request:**
```bash
curl -X GET "http://localhost:8000/api/adm-systems/export?format=csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o adm_systems.csv
```

**Response:** CSV file download
```csv
id,name,business_unit,decision_type,impact_level,compliance_status,created_at
adm_7d3f8a2b,Welfare Payment Eligibility System,Department of Social Services,eligibility,high,compliant,2024-01-15T10:30:00Z
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | Success | GET request successful |
| **201** | Created | Resource created successfully |
| **202** | Accepted | Async task accepted for processing |
| **204** | No Content | DELETE successful |
| **400** | Bad Request | Invalid request parameters |
| **401** | Unauthorized | Missing or invalid authentication token |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource already exists |
| **422** | Unprocessable Entity | Validation error |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Maintenance mode |

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Invalid email format"],
    "password": ["Password must be at least 12 characters"]
  },
  "request_id": "req_abc123",
  "timestamp": "2024-01-16T12:00:00Z"
}
```

### Example Error Responses

**400 Bad Request:**
```bash
curl -X POST "http://localhost:8000/api/adm-systems" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
```

```json
{
  "detail": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "name": ["Field required"],
    "decision_type": ["Field required"],
    "impact_level": ["Field required"]
  }
}
```

**401 Unauthorized:**
```bash
curl -X GET "http://localhost:8000/api/adm-systems"
# No Authorization header
```

```json
{
  "detail": "Not authenticated",
  "error_code": "AUTHENTICATION_REQUIRED"
}
```

**403 Forbidden:**
```bash
# User with 'business_user' role trying to create ADM system
```

```json
{
  "detail": "Insufficient permissions. Required role: privacy_officer or system_admin",
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "required_role": ["privacy_officer", "system_admin"],
  "user_role": "business_user"
}
```

**404 Not Found:**
```bash
curl -X GET "http://localhost:8000/api/adm-systems/nonexistent-id" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{
  "detail": "ADM System not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "resource_type": "adm_system",
  "resource_id": "nonexistent-id"
}
```

**429 Too Many Requests:**
```bash
# After exceeding rate limit
```

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "limit": "60 requests per minute"
}
```

---

## Rate Limiting

### Rate Limits

| User Role | Requests per Minute | Burst Size |
|-----------|---------------------|------------|
| **Anonymous** | 20 | 5 |
| **Authenticated User** | 60 | 10 |
| **Privacy Officer** | 120 | 20 |
| **System Admin** | 300 | 50 |

### Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705406400
```

### Handling Rate Limits

```python
import requests
import time

def make_api_call_with_retry(url, headers):
    max_retries = 3
    retry_delay = 60

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get('X-RateLimit-Reset', time.time() + retry_delay))
            sleep_time = retry_after - time.time()
            print(f"Rate limited. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

---

## Webhooks

### Subscribe to Webhooks

**Endpoint:** `POST /webhooks/subscriptions`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/webhooks/subscriptions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/adm-compliance",
    "events": ["pia.completed", "fairness.bias_detected", "request.submitted"],
    "secret": "your-webhook-secret"
  }'
```

**Response (201 Created):**
```json
{
  "id": "sub_1a2b3c4d",
  "url": "https://your-app.com/webhooks/adm-compliance",
  "events": ["pia.completed", "fairness.bias_detected", "request.submitted"],
  "active": true,
  "created_at": "2024-01-16T12:00:00Z"
}
```

### Webhook Payload Example

**Event: pia.completed**

```json
{
  "event": "pia.completed",
  "timestamp": "2024-01-16T14:30:00Z",
  "data": {
    "pia_id": "pia_1a2b3c4d",
    "adm_system_id": "adm_7d3f8a2b",
    "adm_system_name": "Welfare Payment Eligibility System",
    "overall_risk_level": "medium",
    "pdf_report_url": "https://..."
  }
}
```

### Webhook Signature Verification

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

# In your webhook handler:
signature = request.headers.get('X-Webhook-Signature')
payload = request.body.decode()
secret = "your-webhook-secret"

if verify_webhook_signature(payload, signature, secret):
    # Process webhook
    pass
else:
    # Invalid signature
    return 401
```

---

## Appendix: Code Examples

### Python Client Example

```python
import requests
from typing import Dict, Any

class ADMComplianceClient:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.token = self._login(email, password)

    def _login(self, email: str, password: str) -> str:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_adm_system(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/adm-systems",
            json=data,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def get_adm_system(self, adm_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/adm-systems/{adm_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

# Usage
client = ADMComplianceClient(
    base_url="http://localhost:8000/api",
    email="privacy.officer@example.gov.au",
    password="SecurePassword123!"
)

# Create ADM system
adm_system = client.create_adm_system({
    "name": "Credit Assessment System",
    "decision_type": "risk_assessment",
    "impact_level": "high"
})

print(f"Created ADM system: {adm_system['id']}")
```

### JavaScript/TypeScript Client Example

```typescript
class ADMComplianceAPI {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async login(email: string, password: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    this.token = data.access_token;
  }

  private getHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`
    };
  }

  async createADMSystem(data: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/adm-systems`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error('Failed to create ADM system');
    return response.json();
  }

  async listADMSystems(filters?: any): Promise<any> {
    const params = new URLSearchParams(filters);
    const response = await fetch(
      `${this.baseUrl}/adm-systems?${params}`,
      { headers: this.getHeaders() }
    );

    if (!response.ok) throw new Error('Failed to fetch ADM systems');
    return response.json();
  }
}

// Usage
const api = new ADMComplianceAPI('http://localhost:8000/api');
await api.login('privacy.officer@example.gov.au', 'SecurePassword123!');

const admSystem = await api.createADMSystem({
  name: 'Loan Approval System',
  decision_type: 'eligibility',
  impact_level: 'high'
});
```

---

**Document Version**: 1.0.0
**Last Updated**: 2024-01-XX
**Next Review**: Quarterly
**Maintained by**: API Team
