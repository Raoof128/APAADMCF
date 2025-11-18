# System Architecture

**Australian Privacy Act ADM Compliance Framework**

Version: 1.0.0
Last Updated: 2024-01-XX

---

## Table of Contents

- [Overview](#overview)
- [High-Level Architecture](#high-level-architecture)
- [Component Architecture](#component-architecture)
- [Data Flow Diagrams](#data-flow-diagrams)
- [Database Schema](#database-schema)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Integration Architecture](#integration-architecture)
- [Scalability & Performance](#scalability--performance)

---

## Overview

The Australian Privacy Act ADM Compliance Framework is a full-stack enterprise application designed to help organizations comply with Australian Privacy Act 1988 requirements for automated decision-making systems.

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 15 (database)
- Redis (caching, sessions)
- Celery (async tasks)

**Frontend:**
- React 18
- TypeScript
- Material-UI (MUI)
- React Router v6
- Axios

**Infrastructure:**
- Docker & Docker Compose
- Kubernetes (AKS)
- Terraform (IaC)
- Azure Cloud (Australia East/Southeast)

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile App]
        API_CLIENT[API Clients]
    end

    subgraph "Edge Layer"
        LB[Azure Load Balancer]
        WAF[Web Application Firewall]
        CDN[Azure CDN]
    end

    subgraph "Application Layer"
        NGINX[NGINX Ingress]
        FE[Frontend Container<br/>React + TypeScript]
        BE[Backend API<br/>FastAPI + Python]
        WORKER[Celery Workers]
    end

    subgraph "Service Layer"
        AUTH[Auth Service]
        PIA[PIA Engine]
        FAIR[Fairness Service]
        TRANS[Transparency Gen]
        DRIFT[Drift Detection]
        PDF[PDF Generator]
        NOTIF[Notification Service]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Primary)]
        PG_READ[(PostgreSQL<br/>Read Replica)]
        REDIS[(Redis Cache)]
        BLOB[Azure Blob Storage]
    end

    subgraph "Monitoring & Logging"
        LOGS[Azure Log Analytics]
        METRICS[Azure Monitor]
        ALERTS[Alert Manager]
    end

    WEB --> WAF
    MOBILE --> WAF
    API_CLIENT --> WAF
    WAF --> LB
    LB --> NGINX
    NGINX --> FE
    NGINX --> BE
    FE --> CDN

    BE --> AUTH
    BE --> PIA
    BE --> FAIR
    BE --> TRANS
    BE --> DRIFT
    BE --> PDF
    BE --> NOTIF

    BE --> WORKER
    WORKER --> PIA
    WORKER --> FAIR
    WORKER --> PDF

    AUTH --> REDIS
    AUTH --> PG
    PIA --> PG
    FAIR --> PG
    TRANS --> PG
    DRIFT --> PG
    PDF --> BLOB
    NOTIF --> REDIS

    BE --> PG_READ
    PG --> PG_READ

    BE --> LOGS
    WORKER --> LOGS
    BE --> METRICS
    NGINX --> LOGS
```

### Architecture Principles

1. **Separation of Concerns** - Clear boundaries between presentation, business logic, and data layers
2. **Microservices-Ready** - Service layer designed for future microservices extraction
3. **API-First** - RESTful API with OpenAPI documentation
4. **Stateless Backend** - Horizontal scaling with session data in Redis
5. **Event-Driven** - Async task processing with Celery
6. **Data Sovereignty** - All data stored in Australian Azure regions only
7. **Defense in Depth** - Multiple security layers (WAF, network policies, RBAC, encryption)
8. **Observability** - Comprehensive logging, metrics, and tracing

---

## Component Architecture

### Frontend Architecture

```mermaid
graph TB
    subgraph "React Application"
        APP[App.tsx<br/>Router & Auth Context]

        subgraph "Pages"
            DASH[Dashboard]
            ADM[ADM Registry]
            PIA_PAGE[PIA Management]
            REQ[Requests Portal]
            COMP[Compliance Monitor]
            AUDIT[Audit Logs]
        end

        subgraph "Components"
            LAYOUT[Layout & Navigation]
            FORMS[Form Components]
            TABLES[Data Tables]
            CHARTS[Charts & Metrics]
            MODALS[Dialogs & Modals]
        end

        subgraph "Services"
            API[API Client]
            AUTH_SVC[Auth Service]
            STORAGE[Local Storage]
        end

        subgraph "State Management"
            CONTEXT[React Context]
            HOOKS[Custom Hooks]
        end
    end

    APP --> DASH
    APP --> ADM
    APP --> PIA_PAGE
    APP --> REQ
    APP --> COMP
    APP --> AUDIT

    DASH --> CHARTS
    ADM --> TABLES
    ADM --> FORMS
    PIA_PAGE --> FORMS
    PIA_PAGE --> MODALS

    FORMS --> API
    TABLES --> API
    CHARTS --> API

    API --> AUTH_SVC
    AUTH_SVC --> STORAGE

    CONTEXT --> HOOKS
    HOOKS --> API
```

**Key Frontend Features:**
- **JWT Authentication** - Token-based auth with auto-refresh
- **Role-Based UI** - Components visible based on user role
- **Responsive Design** - Mobile-first Material-UI components
- **Real-Time Updates** - WebSocket connections for live metrics
- **Accessibility** - WCAG 2.1 Level AA compliance
- **Error Boundaries** - Graceful error handling

### Backend Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN[main.py<br/>App Entry Point]

        subgraph "API Routes"
            AUTH_API[/api/auth]
            ADM_API[/api/adm-systems]
            PIA_API[/api/pias]
            FAIR_API[/api/fairness]
            REQ_API[/api/requests]
            COMP_API[/api/compliance]
            AUDIT_API[/api/audit]
            REPORT_API[/api/reports]
        end

        subgraph "Services"
            PIA_SVC[PIA Service]
            FAIR_SVC[Fairness Service]
            TRANS_SVC[Transparency Service]
            DRIFT_SVC[Drift Service]
            PDF_SVC[PDF Generator]
            EMAIL_SVC[Email Service]
        end

        subgraph "Data Access"
            MODELS[SQLAlchemy Models]
            SCHEMAS[Pydantic Schemas]
        end

        subgraph "Middleware"
            CORS[CORS Middleware]
            AUTH_MW[Auth Middleware]
            RATE[Rate Limiting]
            LOG_MW[Logging Middleware]
        end

        subgraph "Utilities"
            VALID[Validators]
            HELPERS[Helper Functions]
            EXCEPT[Exception Handlers]
            CONFIG[Configuration]
        end
    end

    MAIN --> CORS
    MAIN --> AUTH_MW
    MAIN --> RATE
    MAIN --> LOG_MW

    AUTH_API --> MODELS
    ADM_API --> MODELS
    PIA_API --> PIA_SVC
    FAIR_API --> FAIR_SVC
    REQ_API --> MODELS
    COMP_API --> TRANS_SVC
    AUDIT_API --> MODELS
    REPORT_API --> PDF_SVC

    PIA_SVC --> MODELS
    PIA_SVC --> DRIFT_SVC
    FAIR_SVC --> MODELS
    TRANS_SVC --> MODELS
    PDF_SVC --> EMAIL_SVC

    MODELS --> SCHEMAS

    PIA_SVC --> VALID
    FAIR_SVC --> HELPERS
    AUTH_API --> VALID
```

**Key Backend Features:**
- **Async Request Handling** - FastAPI async/await for high concurrency
- **Dependency Injection** - FastAPI dependencies for auth, DB sessions
- **Schema Validation** - Pydantic models for request/response validation
- **Exception Handling** - Custom exception classes with HTTP status codes
- **API Documentation** - Auto-generated OpenAPI/Swagger docs
- **Background Tasks** - Celery for async processing (PDF generation, emails)

---

## Data Flow Diagrams

### Privacy Impact Assessment (PIA) Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant API as Backend API
    participant PIA as PIA Service
    participant DB as PostgreSQL
    participant Worker as Celery Worker
    participant Storage as Blob Storage

    User->>FE: Create PIA for ADM System
    FE->>API: POST /api/pias
    API->>API: Validate JWT Token
    API->>API: Check User Permissions
    API->>PIA: initiate_pia(adm_system_id)
    PIA->>DB: Query ADM System Details
    DB-->>PIA: ADM System Data
    PIA->>DB: Create PIA Record
    PIA->>DB: Create Risk Assessment
    DB-->>PIA: PIA ID
    PIA-->>API: PIA Created
    API-->>FE: 201 Created + PIA Data
    FE-->>User: Display PIA Form

    User->>FE: Complete PIA Assessment
    FE->>API: PUT /api/pias/{id}/complete
    API->>PIA: complete_assessment(pia_id, responses)
    PIA->>PIA: Calculate Risk Scores
    PIA->>PIA: Determine Mitigation Actions
    PIA->>DB: Update PIA Status
    PIA->>Worker: Queue PDF Generation
    Worker->>DB: Fetch PIA Data
    Worker->>Worker: Generate PDF Report
    Worker->>Storage: Upload PDF
    Worker->>DB: Update PIA with PDF URL
    Worker->>API: Notify Completion
    API->>FE: WebSocket: PIA Complete
    FE-->>User: Display Completed PIA + PDF Link
```

### Fairness Assessment Flow

```mermaid
sequenceDiagram
    actor DataScientist as Data Scientist
    participant FE as Frontend
    participant API as Backend API
    participant Fair as Fairness Service
    participant DB as PostgreSQL

    DataScientist->>FE: Upload Prediction Dataset
    FE->>API: POST /api/fairness/assessments
    API->>Fair: create_assessment(adm_id, dataset)
    Fair->>Fair: Validate Dataset Format
    Fair->>Fair: Calculate Demographic Parity
    Fair->>Fair: Calculate Equal Opportunity
    Fair->>Fair: Calculate Predictive Parity
    Fair->>Fair: Calculate Error Rate Ratio
    Fair->>Fair: Identify Bias Patterns
    Fair->>DB: Save Assessment Results
    Fair->>DB: Save Metric Details
    Fair->>DB: Create Recommendations
    DB-->>Fair: Assessment ID
    Fair-->>API: Assessment Complete
    API-->>FE: 200 OK + Results
    FE-->>DataScientist: Display Fairness Metrics

    alt Bias Detected
        Fair->>DB: Create Alert
        Fair->>API: Trigger Notification
        API->>DataScientist: Email: Bias Alert
    end
```

### Individual Rights Request Flow

```mermaid
sequenceDiagram
    actor Individual
    participant Portal as Request Portal
    participant API as Backend API
    participant DB as PostgreSQL
    participant Worker as Celery Worker
    participant Officer as Privacy Officer

    Individual->>Portal: Submit Access Request
    Portal->>API: POST /api/requests
    API->>API: Validate Request Data
    API->>DB: Create Request Record
    API->>DB: Create Audit Log Entry
    DB-->>API: Request ID
    API->>Worker: Queue Identity Verification
    API-->>Portal: 202 Accepted + Tracking ID
    Portal-->>Individual: Request Submitted

    Worker->>Worker: Send Verification Email
    Individual->>Portal: Click Verification Link
    Portal->>API: GET /api/requests/{id}/verify
    API->>DB: Update Request Status
    API->>Officer: Notify: New Verified Request

    Officer->>API: GET /api/requests/{id}
    API->>DB: Fetch Request Details
    DB-->>API: Request Data
    API-->>Officer: Display Request

    Officer->>API: POST /api/requests/{id}/response
    API->>DB: Update Request with Response
    API->>Worker: Queue Response Email
    Worker->>Individual: Email: Response Available

    Individual->>Portal: View Response
    Portal->>API: GET /api/requests/{id}/response
    API->>DB: Log Access Event
    API-->>Portal: Response Data
    Portal-->>Individual: Display Response
```

### Drift Detection Flow

```mermaid
sequenceDiagram
    participant Scheduler as Cron/Scheduler
    participant Worker as Celery Worker
    participant Drift as Drift Service
    participant DB as PostgreSQL
    participant Alert as Alert Service
    participant Team as Operations Team

    Scheduler->>Worker: Run Daily Drift Check
    Worker->>DB: Get Active ADM Systems
    DB-->>Worker: ADM System List

    loop For Each ADM System
        Worker->>Drift: check_drift(adm_id)
        Drift->>DB: Fetch Historical Metrics
        Drift->>DB: Fetch Current Metrics
        Drift->>Drift: Calculate PSI (Data Drift)
        Drift->>Drift: Calculate KS Statistic
        Drift->>Drift: Calculate Performance Drift

        alt Drift Detected
            Drift->>DB: Create Drift Alert
            Drift->>DB: Log Drift Metrics
            Drift->>Alert: Send Alert
            Alert->>Team: Email/SMS: Drift Detected
            Alert->>DB: Update Alert Status
        else No Drift
            Drift->>DB: Log Normal Status
        end
    end

    Worker->>DB: Update Last Check Timestamp
```

---

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : creates
    USERS ||--o{ INDIVIDUAL_REQUESTS : submits
    USERS {
        uuid id PK
        string email UK
        string hashed_password
        enum role
        timestamp created_at
    }

    ADM_SYSTEMS ||--o{ PIAS : has
    ADM_SYSTEMS ||--o{ FAIRNESS_ASSESSMENTS : has
    ADM_SYSTEMS ||--o{ DRIFT_ALERTS : has
    ADM_SYSTEMS ||--o{ TRANSPARENCY_NOTICES : has
    ADM_SYSTEMS {
        uuid id PK
        string name
        enum decision_type
        enum impact_level
        jsonb metadata
        timestamp created_at
    }

    PIAS ||--o{ PIA_RISK_ASSESSMENTS : contains
    PIAS ||--o{ PIA_MITIGATION_ACTIONS : requires
    PIAS {
        uuid id PK
        uuid adm_system_id FK
        enum status
        timestamp completed_at
        string pdf_report_url
    }

    PIA_RISK_ASSESSMENTS {
        uuid id PK
        uuid pia_id FK
        string risk_category
        enum severity
        text description
        float likelihood
        float impact_score
    }

    FAIRNESS_ASSESSMENTS ||--o{ FAIRNESS_METRICS : contains
    FAIRNESS_ASSESSMENTS {
        uuid id PK
        uuid adm_system_id FK
        timestamp assessed_at
        jsonb dataset_stats
        float overall_fairness_score
    }

    FAIRNESS_METRICS {
        uuid id PK
        uuid assessment_id FK
        string metric_name
        string protected_attribute
        float metric_value
        boolean passes_threshold
    }

    INDIVIDUAL_REQUESTS ||--o{ REQUEST_RESPONSES : has
    INDIVIDUAL_REQUESTS {
        uuid id PK
        uuid user_id FK
        enum request_type
        enum status
        timestamp submitted_at
        timestamp due_date
        boolean verified
    }

    DRIFT_ALERTS {
        uuid id PK
        uuid adm_system_id FK
        enum drift_type
        float severity_score
        timestamp detected_at
        boolean resolved
    }

    COMPLIANCE_CHECKS {
        uuid id PK
        uuid adm_system_id FK
        enum check_type
        enum result
        timestamp checked_at
        jsonb findings
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        jsonb details
        timestamp timestamp
        string ip_address
    }
```

### Database Design Principles

1. **Normalization** - 3NF with strategic denormalization for performance
2. **UUID Primary Keys** - Globally unique, non-sequential IDs
3. **Immutable Audit Logs** - PostgreSQL rules prevent modification/deletion
4. **JSONB for Flexibility** - Structured yet flexible metadata storage
5. **Temporal Data** - Created/updated timestamps on all entities
6. **Referential Integrity** - Foreign keys with cascade rules
7. **Indexes** - Strategic indexes on frequently queried columns
8. **Partitioning** - Audit logs partitioned by month
9. **Full-Text Search** - GIN indexes for text search
10. **Materialized Views** - Pre-computed compliance dashboard metrics

---

## Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "Perimeter Security"
        WAF[Web Application Firewall]
        DDoS[DDoS Protection]
        TLS[TLS 1.3 Encryption]
    end

    subgraph "Network Security"
        NSG[Network Security Groups]
        VNET[Virtual Network Isolation]
        PE[Private Endpoints]
    end

    subgraph "Application Security"
        JWT[JWT Authentication]
        RBAC[Role-Based Access Control]
        RATE_LIM[Rate Limiting]
        CSRF[CSRF Protection]
    end

    subgraph "Data Security"
        ENC_REST[Encryption at Rest]
        ENC_TRANSIT[Encryption in Transit]
        KMS[Key Management Service]
        MASK[Data Masking]
    end

    subgraph "Audit & Compliance"
        AUDIT[Immutable Audit Logs]
        MONITOR[Security Monitoring]
        ALERT[Security Alerts]
        SIEM[SIEM Integration]
    end

    WAF --> NSG
    DDoS --> NSG
    TLS --> NSG

    NSG --> JWT
    VNET --> RBAC
    PE --> RATE_LIM

    JWT --> ENC_REST
    RBAC --> ENC_TRANSIT
    RATE_LIM --> KMS
    CSRF --> MASK

    ENC_REST --> AUDIT
    KMS --> MONITOR
    MASK --> ALERT
    AUDIT --> SIEM
```

### Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant API as Auth API
    participant DB as PostgreSQL
    participant Redis as Redis Cache

    User->>FE: Enter Credentials
    FE->>API: POST /api/auth/login
    API->>DB: Query User by Email
    DB-->>API: User Record
    API->>API: Verify Password Hash
    API->>API: Generate JWT Token
    API->>Redis: Store Session Data
    API-->>FE: JWT Token + Refresh Token
    FE->>FE: Store Tokens in Memory
    FE-->>User: Redirect to Dashboard

    loop Every API Request
        FE->>API: Request + JWT Header
        API->>API: Validate JWT Signature
        API->>API: Check Token Expiry
        API->>Redis: Verify Session Active
        alt Token Valid
            API->>API: Extract User Claims
            API->>API: Check RBAC Permissions
            API-->>FE: Process Request
        else Token Invalid/Expired
            API-->>FE: 401 Unauthorized
            FE->>API: POST /api/auth/refresh
            API->>API: Validate Refresh Token
            API->>API: Issue New JWT
            API-->>FE: New JWT Token
        end
    end
```

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|------------|
| **System Administrator** | Full system access, user management, configuration |
| **Privacy Officer** | PIA management, compliance oversight, reports |
| **Data Scientist** | Fairness assessments, drift monitoring, model metrics |
| **Auditor** | Read-only access to all data, audit logs, reports |
| **Business User** | View ADM systems, request transparency notices |
| **Individual** | Submit rights requests, view own data, track requests |

### Data Encryption

**Encryption at Rest:**
- PostgreSQL: Transparent Data Encryption (TDE)
- Azure Blob Storage: AES-256 encryption
- Secrets: Azure Key Vault with HSM backing

**Encryption in Transit:**
- TLS 1.3 for all HTTPS connections
- Certificate pinning in mobile apps
- Mutual TLS for service-to-service communication

---

## Deployment Architecture

### Azure Kubernetes Service (AKS) Deployment

```mermaid
graph TB
    subgraph "Azure Region: Australia East"
        subgraph "AKS Cluster"
            subgraph "Ingress Namespace"
                INGRESS[NGINX Ingress Controller]
                CERT[Cert Manager]
            end

            subgraph "Application Namespace"
                FE_POD1[Frontend Pod 1]
                FE_POD2[Frontend Pod 2]
                BE_POD1[Backend Pod 1]
                BE_POD2[Backend Pod 2]
                BE_POD3[Backend Pod 3]
                WORKER_POD1[Worker Pod 1]
                WORKER_POD2[Worker Pod 2]
            end

            subgraph "Data Namespace"
                REDIS_POD[Redis Pod]
            end
        end

        subgraph "Azure Services"
            PG_FLEX[(PostgreSQL Flexible Server)]
            PG_REPLICA[(Read Replica)]
            KV[Key Vault]
            STORAGE[Blob Storage]
            LOG[Log Analytics]
        end
    end

    subgraph "Azure Region: Australia Southeast"
        PG_GEO[(PostgreSQL Geo-Replica)]
        STORAGE_GEO[Blob Storage Geo-Replica]
    end

    INGRESS --> FE_POD1
    INGRESS --> FE_POD2
    INGRESS --> BE_POD1
    INGRESS --> BE_POD2
    INGRESS --> BE_POD3

    BE_POD1 --> REDIS_POD
    BE_POD2 --> REDIS_POD
    BE_POD3 --> REDIS_POD

    BE_POD1 --> PG_FLEX
    BE_POD2 --> PG_FLEX
    BE_POD3 --> PG_FLEX

    WORKER_POD1 --> PG_FLEX
    WORKER_POD2 --> PG_FLEX

    PG_FLEX --> PG_REPLICA
    PG_FLEX --> PG_GEO

    BE_POD1 --> KV
    BE_POD2 --> KV
    BE_POD3 --> KV

    BE_POD1 --> STORAGE
    WORKER_POD1 --> STORAGE

    STORAGE --> STORAGE_GEO

    FE_POD1 --> LOG
    BE_POD1 --> LOG
    WORKER_POD1 --> LOG
```

### Container Specifications

**Frontend Container:**
```yaml
Image: adm-compliance-frontend:1.0.0
Resources:
  CPU: 500m - 1000m
  Memory: 512Mi - 1Gi
Replicas: 2-10 (HPA)
Health Checks:
  Liveness: HTTP GET / (30s interval)
  Readiness: HTTP GET /health (10s interval)
```

**Backend Container:**
```yaml
Image: adm-compliance-backend:1.0.0
Resources:
  CPU: 1000m - 2000m
  Memory: 2Gi - 4Gi
Replicas: 3-20 (HPA based on CPU/Memory)
Health Checks:
  Liveness: HTTP GET /health (30s interval)
  Readiness: HTTP GET /health/ready (10s interval)
Environment:
  - DATABASE_URL (from Secret)
  - REDIS_URL (from Secret)
  - JWT_SECRET (from Key Vault)
```

**Worker Container:**
```yaml
Image: adm-compliance-worker:1.0.0
Resources:
  CPU: 2000m - 4000m
  Memory: 4Gi - 8Gi
Replicas: 2-10 (HPA based on queue depth)
Queue: Celery with Redis broker
Tasks:
  - PDF Generation (high priority)
  - Email Sending (medium priority)
  - Drift Detection (scheduled)
  - Report Generation (low priority)
```

---

## Integration Architecture

### External System Integrations

```mermaid
graph LR
    subgraph "ADM Compliance Framework"
        API[REST API]
        WEBHOOK[Webhook Handler]
        EXPORT[Export Service]
    end

    subgraph "Identity Providers"
        AAD[Azure AD]
        SAML[SAML IdP]
    end

    subgraph "Notification Systems"
        SMTP[Email Server]
        SMS[SMS Gateway]
        TEAMS[Microsoft Teams]
    end

    subgraph "Data Sources"
        ML_PLATFORM[ML Platform APIs]
        DATA_LAKE[Data Lake]
        SIEM_SYS[SIEM System]
    end

    subgraph "Reporting Tools"
        BI[Power BI]
        TABLEAU[Tableau]
    end

    AAD --> API
    SAML --> API

    API --> SMTP
    API --> SMS
    API --> TEAMS

    ML_PLATFORM --> WEBHOOK
    DATA_LAKE --> API
    API --> SIEM_SYS

    EXPORT --> BI
    EXPORT --> TABLEAU
```

### API Integration Patterns

**Inbound Integrations:**
- RESTful API with OpenAPI 3.0 spec
- Webhook endpoints for event notifications
- Bulk data import via CSV/JSON upload
- SAML/OAuth2 for SSO authentication

**Outbound Integrations:**
- Webhook notifications for critical events
- Email/SMS notifications via configurable providers
- SIEM integration via syslog/CEF format
- Export API for BI tools (JSON, CSV, Parquet)

---

## Scalability & Performance

### Horizontal Scaling Strategy

```mermaid
graph TB
    subgraph "Load Distribution"
        LB[Load Balancer]

        subgraph "Frontend Tier (Stateless)"
            FE1[Frontend 1]
            FE2[Frontend 2]
            FEN[Frontend N]
        end

        subgraph "Backend Tier (Stateless)"
            BE1[Backend 1]
            BE2[Backend 2]
            BEN[Backend N]
        end

        subgraph "Worker Tier (Queue-Based)"
            W1[Worker 1]
            W2[Worker 2]
            WN[Worker N]
        end
    end

    subgraph "Data Tier"
        PG_PRIMARY[(Primary DB<br/>Writes)]
        PG_READ1[(Read Replica 1)]
        PG_READ2[(Read Replica 2)]
        REDIS_CLUSTER[(Redis Cluster<br/>3 Masters, 3 Replicas)]
    end

    LB --> FE1
    LB --> FE2
    LB --> FEN

    FE1 --> BE1
    FE1 --> BE2
    FE2 --> BEN

    BE1 --> PG_PRIMARY
    BE2 --> PG_PRIMARY
    BEN --> PG_PRIMARY

    BE1 --> PG_READ1
    BE2 --> PG_READ2
    BEN --> PG_READ1

    BE1 --> REDIS_CLUSTER
    BE2 --> REDIS_CLUSTER
    BEN --> REDIS_CLUSTER

    W1 --> PG_PRIMARY
    W2 --> PG_PRIMARY
    WN --> PG_PRIMARY

    W1 --> REDIS_CLUSTER
    W2 --> REDIS_CLUSTER
```

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time** | < 200ms (p95) | All GET endpoints |
| **API Response Time** | < 500ms (p95) | POST/PUT endpoints |
| **Page Load Time** | < 2s | Frontend initial load |
| **Database Queries** | < 50ms (p95) | Simple queries |
| **Concurrent Users** | 10,000+ | Simultaneous active sessions |
| **Throughput** | 1,000 req/s | API requests per second |
| **Availability** | 99.9% | Annual uptime SLA |
| **PDF Generation** | < 30s | PIA report generation |
| **Fairness Assessment** | < 5min | 100k record dataset |

### Caching Strategy

**Redis Cache Layers:**
1. **Session Cache** - User sessions, JWT blacklist (TTL: 1 hour)
2. **Query Cache** - Frequently accessed data (TTL: 5 minutes)
3. **API Response Cache** - GET endpoint responses (TTL: 1 minute)
4. **Computed Metrics** - Dashboard statistics (TTL: 10 minutes)

**CDN Caching:**
- Static assets (JS, CSS, images): 1 year
- API responses (read-only): 1 minute
- HTML pages: No cache (dynamic)

### Database Optimization

**Read/Write Splitting:**
- All writes → Primary database
- Read queries → Round-robin across read replicas
- Dashboard queries → Materialized views

**Connection Pooling:**
- Backend: PgBouncer (100 max connections)
- Workers: Direct connections (20 max per worker)
- Pool mode: Transaction pooling

**Query Optimization:**
- Prepared statements for common queries
- Index coverage for WHERE/JOIN clauses
- EXPLAIN ANALYZE on slow queries (>100ms)
- Automatic query plan caching

---

## Monitoring & Observability

### Observability Stack

```mermaid
graph TB
    subgraph "Application"
        APP[Application Code]
        LOGS_LIB[Logging Library]
        METRICS_LIB[Prometheus Client]
        TRACE_LIB[OpenTelemetry]
    end

    subgraph "Collection"
        FLUENTD[Fluentd]
        PROMETHEUS[Prometheus]
        JAEGER[Jaeger]
    end

    subgraph "Storage"
        LOG_STORE[Azure Log Analytics]
        METRICS_STORE[Azure Monitor]
        TRACE_STORE[Jaeger Backend]
    end

    subgraph "Visualization"
        GRAFANA[Grafana Dashboards]
        AZURE_DASH[Azure Dashboards]
        ALERTS[Alert Manager]
    end

    APP --> LOGS_LIB
    APP --> METRICS_LIB
    APP --> TRACE_LIB

    LOGS_LIB --> FLUENTD
    METRICS_LIB --> PROMETHEUS
    TRACE_LIB --> JAEGER

    FLUENTD --> LOG_STORE
    PROMETHEUS --> METRICS_STORE
    JAEGER --> TRACE_STORE

    LOG_STORE --> GRAFANA
    METRICS_STORE --> GRAFANA
    TRACE_STORE --> GRAFANA

    METRICS_STORE --> AZURE_DASH
    LOG_STORE --> AZURE_DASH

    METRICS_STORE --> ALERTS
```

### Key Metrics Monitored

**Application Metrics:**
- Request rate, error rate, duration (RED method)
- Endpoint-specific latency percentiles (p50, p95, p99)
- Active user sessions
- Background job queue depth and processing time
- Cache hit/miss ratios

**Infrastructure Metrics:**
- CPU, memory, disk usage per pod
- Network I/O and bandwidth
- Database connection pool utilization
- Redis memory usage and eviction rate
- Storage IOPS and latency

**Business Metrics:**
- Active ADM systems count
- PIAs completed per day
- Fairness assessments with bias detected
- Individual requests by type and status
- Compliance check pass/fail rates

---

## Disaster Recovery

### Backup Strategy

**Database Backups:**
- Full backup: Daily at 02:00 AEST
- Differential backup: Every 6 hours
- Transaction log backup: Every 15 minutes
- Retention: 30 days standard, 7 years for audit logs
- Geographic replication to Australia Southeast

**Application Backups:**
- Infrastructure as Code (Terraform state): Daily backup to versioned storage
- Configuration: Stored in Git with encrypted secrets
- Blob storage: Geo-redundant with cross-region replication

### Recovery Objectives

| Scenario | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|----------|-------------------------------|-------------------------------|
| **Pod Failure** | < 1 minute | 0 (no data loss) |
| **Node Failure** | < 5 minutes | 0 (no data loss) |
| **AZ Failure** | < 15 minutes | < 5 minutes |
| **Region Failure** | < 4 hours | < 1 hour |
| **Database Corruption** | < 2 hours | < 15 minutes |
| **Complete System Loss** | < 8 hours | < 1 hour |

---

## Compliance & Data Sovereignty

### Australian Data Residency

**Data Storage Locations:**
- **Primary Region**: Azure Australia East (New South Wales)
- **Secondary Region**: Azure Australia Southeast (Victoria)
- **Prohibited Regions**: All non-Australian regions

**Data Flow Controls:**
- Network policies prevent data egress to non-AU regions
- Azure Policy enforces resource location constraints
- Terraform validation ensures AU-only deployments

### Audit Requirements

**Audit Log Capture:**
- All user authentication events
- All data access and modifications
- All administrative actions
- All API calls with parameters
- All failed authorization attempts

**Audit Log Properties:**
- Immutable (cannot be modified or deleted)
- Tamper-evident (checksums and timestamps)
- Retention: 7 years minimum
- Export capability for legal discovery

---

## Future Architecture Considerations

### Planned Enhancements

1. **Microservices Migration** - Gradual extraction of services (PIA, Fairness, etc.)
2. **Event-Driven Architecture** - Implement Event Bus (Azure Event Grid)
3. **GraphQL API** - Add GraphQL layer for flexible client queries
4. **Real-Time Dashboards** - WebSocket-based live metrics updates
5. **Mobile Applications** - Native iOS/Android apps
6. **AI-Assisted PIAs** - ML models to suggest risk assessments
7. **Blockchain Audit Trail** - Immutable audit log using distributed ledger
8. **Multi-Tenancy** - Support multiple organizations in single instance

---

## Appendices

### A. Technology Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI over Django** | Async performance, modern Python, auto-documentation |
| **PostgreSQL over MongoDB** | ACID compliance, relational data, mature ecosystem |
| **React over Angular** | Component reusability, large ecosystem, team expertise |
| **AKS over VMs** | Container orchestration, auto-scaling, easier deployments |
| **Redis over Memcached** | Richer data structures, persistence, pub/sub support |

### B. Design Patterns Used

- **Repository Pattern** - Data access abstraction
- **Service Layer Pattern** - Business logic separation
- **Factory Pattern** - Object creation (Pydantic schemas)
- **Dependency Injection** - FastAPI dependencies
- **Observer Pattern** - Event notifications
- **Strategy Pattern** - Pluggable fairness metrics
- **Singleton Pattern** - Database connection pool

### C. References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [OAIC Guidelines on Automated Decision-Making](https://www.oaic.gov.au/)
- [Australian Privacy Act 1988](https://www.legislation.gov.au/Series/C2004A03712)

---

**Document Control:**
- **Version**: 1.0.0
- **Last Updated**: 2024-01-XX
- **Author**: Architecture Team
- **Reviewers**: Security Team, Privacy Officer, CTO
- **Next Review**: Quarterly
