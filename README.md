# Australian Privacy Act Automated Decision-Making Compliance Framework

A comprehensive, production-ready platform for assessing, monitoring, documenting, and demonstrating compliance for automated decision-making (ADM) systems under the Australian Privacy Act 1988 and OAIC guidance.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Compliance](#compliance)
- [Contributing](#contributing)
- [License](#license)

## Overview

This framework helps Australian organisations ensure their automated decision-making systems comply with:

- **Australian Privacy Act 1988**
- **Australian Privacy Principles (APPs)** - especially APP1, APP3, APP5, APP6, APP10, APP11, APP13
- **OAIC Guidance** on automated decision-making, profiling, and high-risk processing
- **AI Ethics Principles** - transparency, contestability, auditability, fairness

### Key Capabilities

1. **ADM System Registry** - Central catalogue of all automated decision systems
2. **Privacy Impact Assessments** - Automated PIA workflows with APP compliance checks
3. **Fairness & Bias Testing** - Quantitative fairness metrics and explainability (SHAP/LIME)
4. **Transparency Notices** - Generate APP5-compliant transparency notices
5. **Individual Rights** - Handle explanation, review, correction, and access requests
6. **Continuous Monitoring** - Drift detection, bias monitoring, compliance alerts
7. **Audit & Governance** - Immutable audit logs and OAIC-ready reporting

## Features

### Core Functionality

✅ **ADM System Registry**
- Catalogue all decision systems (ML models, rule engines, scoring systems)
- Classify by impact level (low/medium/high/critical)
- Track deployment status and review cycles
- Link to PIAs, fairness assessments, and data categories

✅ **Privacy Impact Assessment Engine**
- Purpose & necessity test
- Data minimisation assessment (APP3)
- Consent & notification analysis (APP5)
- Reasonable expectations evaluation
- Sensitive information handling (special categories)
- Risk identification and mitigation workflow
- Approval and versioning

✅ **Fairness & Bias Assessment**
- Demographic parity
- Equal opportunity
- Predictive parity
- Error rate ratios
- Disparate impact analysis
- SHAP/LIME explainability (demo mode)
- Fairness score calculation (0-100)
- High-risk flagging and recommendations

✅ **Transparency & Notifications**
- APP5-compliant collection notices
- Automated decision explanations
- Individual rights information
- Review process documentation
- Machine-readable metadata (JSON-LD)

✅ **Individual Request Handling**
- Explanation requests
- Human review requests
- Correction requests (APP13)
- Access requests (APP12)
- Complaint handling
- SLA tracking (30-day default)
- Request history and audit trail

✅ **Continuous Compliance Monitoring**
- Data drift detection (PSI, KS test)
- Model drift monitoring
- Concept drift analysis
- Fairness metric monitoring
- Automated alerts (critical/warning/info)
- Compliance dashboard

✅ **Audit & Governance**
- Immutable audit logs
- Activity tracking (all CRUD operations)
- Compliance summary reports
- OAIC-ready governance reports
- Internal risk committee reports
- Fairness audit reports
- Model cards for transparency

### Security & Privacy

🔒 **Australian Data Sovereignty**
- All infrastructure in Azure Australia East/Southeast
- No data transfer outside Australia
- Compliance with Australian data residency requirements

🔒 **Encryption**
- AES-256 encryption at rest
- TLS 1.2+ in transit
- Secrets in Azure Key Vault
- Database encryption enabled

🔒 **Access Control**
- Role-based access control (RBAC)
- Six roles: Admin, Privacy Officer, Compliance Auditor, Data Scientist, Request Manager, Read-Only Viewer
- JWT token authentication
- Session management

🔒 **Audit Trail**
- Immutable audit logs (cannot be deleted/modified)
- User activity tracking
- Resource access history
- Change tracking with before/after values

## Architecture

### Tech Stack

**Backend:**
- Python 3.11
- FastAPI - Modern async web framework
- PostgreSQL 15 - Relational database
- SQLAlchemy - ORM
- Pydantic - Data validation
- WeasyPrint - PDF generation
- SHAP/LIME - Model explainability (demo mode)
- Pandas/NumPy/SciPy - Data analysis

**Frontend:**
- React 18
- Material-UI (MUI)
- React Router
- Axios - HTTP client
- Recharts - Data visualization

**Infrastructure:**
- Docker & Docker Compose
- Azure Kubernetes Service (AKS)
- Azure PostgreSQL Flexible Server
- Azure Key Vault
- Azure Storage (Blob)
- Azure Application Gateway with WAF
- Terraform - Infrastructure as Code
- GitHub Actions - CI/CD

**Monitoring:**
- Azure Log Analytics
- Application Insights
- PostgreSQL query performance insights

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Azure Application Gateway                    │
│                    (WAF, TLS Termination)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
             ┌───────────────┴────────────────┐
             │                                │
┌────────────▼─────────────┐    ┌────────────▼──────────────┐
│   React Frontend (SPA)   │    │   FastAPI Backend API     │
│   - Material-UI          │    │   - REST API              │
│   - Role-based access    │    │   - Authentication        │
│   - Dashboards           │    │   - Business logic        │
└────────────┬─────────────┘    └────────────┬──────────────┘
             │                                │
             └───────────────┬────────────────┘
                             │
             ┌───────────────┴────────────────┐
             │                                │
┌────────────▼─────────────┐    ┌────────────▼──────────────┐
│  PostgreSQL Database     │    │   Azure Blob Storage      │
│  - ADM systems           │    │   - Evidence files        │
│  - PIAs, risks           │    │   - Generated reports     │
│  - Audit logs            │    │   - Uploads               │
│  - Individual requests   │    └───────────────────────────┘
└──────────────────────────┘
```

### Database Schema

The database includes 18+ tables:

- **Core:** `users`, `adm_systems`, `data_categories`
- **PIA:** `pia_assessments`, `risk_items`, `mitigation_tasks`, `evidence_items`
- **Fairness:** `fairness_assessments`, `explainability_results`
- **Requests:** `individual_requests`, `request_history`
- **Compliance:** `compliance_alerts`, `drift_detections`
- **Governance:** `audit_logs`, `transparency_notices`, `workflows`, `compliance_reports`

See [backend/database_schema.sql](backend/database_schema.sql) for the complete schema.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (for local development without Docker)
- Azure CLI (for Azure deployment)
- Terraform 1.0+ (for infrastructure deployment)

### Local Development with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/APAADMCF.git
cd APAADMCF
```

2. **Set up environment variables:**

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start all services:**

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- React frontend (port 3000)
- Redis cache (port 6379)
- PgAdmin (port 5050) - optional

4. **Access the application:**

- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs
- PgAdmin: http://localhost:5050 (optional)

5. **Default credentials:**

```
Email: admin@example.gov.au
Password: Admin123!
```

⚠️ **IMPORTANT:** Change default credentials immediately in production!

### Local Development without Docker

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb adm_compliance
psql adm_compliance < database_schema.sql

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Deployment

### Azure Deployment

1. **Set up Azure credentials:**

```bash
az login
az account set --subscription "your-subscription-id"
```

2. **Initialize Terraform:**

```bash
cd infrastructure/terraform
terraform init
```

3. **Review and apply infrastructure:**

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

4. **Deploy application:**

```bash
# Build and push Docker images
docker build -t youracr.azurecr.io/adm-backend:latest ./backend
docker build -t youracr.azurecr.io/adm-frontend:latest ./frontend

docker push youracr.azurecr.io/adm-backend:latest
docker push youracr.azurecr.io/adm-frontend:latest

# Deploy to AKS
kubectl apply -f k8s/
```

See [docs/deployment.md](docs/deployment.md) for detailed deployment instructions.

## API Documentation

### Interactive API Documentation

Once the backend is running, visit:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

**ADM System Registry:**
- `GET /api/v1/adm/registry` - List ADM systems
- `POST /api/v1/adm/registry` - Register new ADM system
- `GET /api/v1/adm/registry/{id}` - Get ADM system details
- `PUT /api/v1/adm/registry/{id}` - Update ADM system
- `DELETE /api/v1/adm/registry/{id}` - Decommission ADM system

**Privacy Impact Assessments:**
- `POST /api/v1/pia/start` - Start new PIA
- `GET /api/v1/pia` - List PIAs
- `GET /api/v1/pia/{id}` - Get PIA details
- `PUT /api/v1/pia/{id}` - Update PIA
- `POST /api/v1/pia/{id}/approve` - Approve/reject PIA
- `GET /api/v1/pia/{id}/report` - Generate PIA PDF report

**Fairness & Bias:**
- `POST /api/v1/fairness/{adm_system_id}/assess` - Run fairness assessment
- `GET /api/v1/fairness/{adm_system_id}/assessments` - List assessments
- `POST /api/v1/fairness/{adm_system_id}/explainability` - Generate SHAP/LIME

**Transparency:**
- `POST /api/v1/transparency/notice` - Generate APP5 notice
- `GET /api/v1/transparency/notice/{adm_system_id}` - Get active notice (public)
- `GET /api/v1/transparency/notice/{adm_system_id}/metadata` - Get metadata (public)

**Individual Requests:**
- `POST /api/v1/requests` - Submit request (public)
- `GET /api/v1/requests` - List requests
- `GET /api/v1/requests/{id}` - Get request details
- `POST /api/v1/requests/{id}/assign` - Assign request
- `PUT /api/v1/requests/{id}/status` - Update status
- `POST /api/v1/requests/{id}/review` - Complete human review

**Compliance Monitoring:**
- `GET /api/v1/compliance/alerts` - List compliance alerts
- `PUT /api/v1/compliance/alerts/{id}/acknowledge` - Acknowledge alert
- `PUT /api/v1/compliance/alerts/{id}/resolve` - Resolve alert
- `GET /api/v1/compliance/drift` - List drift detections
- `POST /api/v1/compliance/drift/{adm_system_id}/detect` - Run drift detection
- `GET /api/v1/compliance/dashboard` - Get compliance dashboard

**Audit & Governance:**
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /api/v1/audit/logs/export` - Export audit logs
- `GET /api/v1/audit/activity/user/{user_id}` - User activity summary
- `GET /api/v1/audit/compliance/summary` - Compliance summary

**Reports:**
- `POST /api/v1/reports/oaic` - Generate OAIC report
- `POST /api/v1/reports/internal` - Generate internal report
- `POST /api/v1/reports/fairness-audit/{adm_system_id}` - Fairness audit report
- `GET /api/v1/reports/model-card/{adm_system_id}` - Generate model card

## Compliance

### Australian Privacy Act 1988

This framework helps organisations comply with key Australian Privacy Principles (APPs):

- **APP 1** - Open and transparent management of personal information
- **APP 3** - Collection of solicited personal information (data minimisation)
- **APP 5** - Notification of collection
- **APP 6** - Use or disclosure of personal information
- **APP 10** - Quality of personal information
- **APP 11** - Security of personal information
- **APP 12** - Access to personal information
- **APP 13** - Correction of personal information

### OAIC Guidance

Implements OAIC guidance on:
- Automated decision-making transparency
- High-risk processing
- Profiling and inference
- Individual rights (explanation, review, correction)
- Privacy impact assessments

### AI Ethics Principles

Aligned with Australia's AI Ethics Framework:
- **Transparency & Explainability** - Model cards, SHAP/LIME explanations
- **Fairness** - Bias detection and fairness metrics
- **Accountability** - Audit logs and governance reports
- **Contestability** - Human review of automated decisions

## Demo Mode

The platform includes demo mode for testing without real ML models:

**Synthetic Data Generation:**
```bash
python demo/scripts/generate_synthetic_data.py
```

**Demo Workflows:**
```bash
# Complete demo workflow
python demo/scripts/demo_workflow.py

# Individual demos
python demo/scripts/demo_pia.py
python demo/scripts/demo_fairness.py
python demo/scripts/demo_requests.py
```

## Project Structure

```
APAADMCF/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, security, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/            # Backend tests
│   ├── database_schema.sql
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API clients
│   │   └── utils/        # Utilities
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   ├── terraform/        # Azure infrastructure
│   └── ansible/          # Configuration management
├── docs/                 # Documentation
│   ├── architecture.md
│   ├── deployment.md
│   ├── privacy-act-adm.md
│   └── methodology/
├── demo/                 # Demo scripts and data
│   ├── datasets/
│   ├── models/
│   └── scripts/
├── .github/
│   └── workflows/        # CI/CD pipelines
├── docker-compose.yml
└── README.md
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/APAADMCF/issues
- Documentation: https://docs.example.com
- Email: support@example.com

## Acknowledgments

- Australian Privacy Principles (APPs)
- Office of the Australian Information Commissioner (OAIC)
- Australia's AI Ethics Framework
- FastAPI framework
- React and Material-UI communities

---

**⚠️ Disclaimer:** This framework is provided as-is to assist with compliance efforts. It does not constitute legal advice. Organisations should consult with legal counsel and privacy professionals to ensure full compliance with applicable laws and regulations.
