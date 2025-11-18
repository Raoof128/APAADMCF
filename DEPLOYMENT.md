# Deployment Runbook

**Australian Privacy Act ADM Compliance Framework**

Version: 1.0.0
Last Updated: 2024-01-XX

---

## Table of Contents

- [Overview](#overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Local Development Deployment](#local-development-deployment)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Azure Production Deployment](#azure-production-deployment)
- [Database Migration](#database-migration)
- [Configuration Management](#configuration-management)
- [Health Checks & Validation](#health-checks--validation)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)
- [Post-Deployment Tasks](#post-deployment-tasks)

---

## Overview

This runbook provides step-by-step procedures for deploying the ADM Compliance Framework across different environments.

### Deployment Environments

| Environment | Purpose | Infrastructure | Database | URL |
|-------------|---------|---------------|----------|-----|
| **Local** | Developer workstation | Docker Compose | PostgreSQL container | http://localhost:3000 |
| **Staging** | Pre-production testing | Azure AKS (1 node) | PostgreSQL Flexible (Dev tier) | https://staging.adm-compliance.gov.au |
| **Production** | Live system | Azure AKS (3+ nodes) | PostgreSQL Flexible (HA) | https://adm-compliance.gov.au |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Deployment Pipeline                     │
├─────────────────────────────────────────────────────────┤
│ 1. Code Push to GitHub                                  │
│         ↓                                               │
│ 2. GitHub Actions CI/CD                                 │
│         ↓                                               │
│ 3. Build & Test (Pytest, Linting, Security Scan)       │
│         ↓                                               │
│ 4. Build Docker Images                                  │
│         ↓                                               │
│ 5. Push to Azure Container Registry                     │
│         ↓                                               │
│ 6. Deploy to AKS (Kubectl/Helm)                         │
│         ↓                                               │
│ 7. Run Database Migrations                              │
│         ↓                                               │
│ 8. Health Checks & Smoke Tests                          │
│         ↓                                               │
│ 9. Production Traffic Switch                            │
└─────────────────────────────────────────────────────────┘
```

---

## Pre-Deployment Checklist

### Required Tools

Verify all required tools are installed:

```bash
# Check versions
python --version        # Required: Python 3.11+
node --version          # Required: Node 18+
docker --version        # Required: Docker 24+
docker-compose --version # Required: Docker Compose 2.20+
terraform --version     # Required: Terraform 1.5+ (for production)
kubectl version        # Required: kubectl 1.27+ (for production)
az --version           # Required: Azure CLI 2.50+ (for production)
```

### Access Requirements

- [ ] GitHub repository access with write permissions
- [ ] Azure subscription access (for production)
- [ ] Azure Container Registry push permissions
- [ ] AKS cluster admin access
- [ ] PostgreSQL database admin credentials
- [ ] Azure Key Vault secrets access
- [ ] DNS management access (for production)

### Security Prerequisites

- [ ] SSL/TLS certificates obtained and validated
- [ ] Azure AD app registration completed (for SSO)
- [ ] JWT signing keys generated and stored in Key Vault
- [ ] Database encryption keys provisioned
- [ ] Service principal created with minimal permissions
- [ ] Network security groups configured
- [ ] Firewall rules defined

### Code Readiness

- [ ] All tests passing (100% success rate)
- [ ] Code review completed and approved
- [ ] Security scan passed (no critical/high vulnerabilities)
- [ ] Database migrations tested on staging
- [ ] Breaking changes documented
- [ ] Rollback plan prepared
- [ ] Change request approved (for production)

---

## Environment Setup

### Environment Variables

Create environment-specific `.env` files:

**Development (.env.development):**
```bash
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=adm_compliance_dev
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres123

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Frontend
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development

# Email (Development - Console only)
SMTP_ENABLED=false
EMAIL_BACKEND=console

# File Storage
FILE_STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage
```

**Staging (.env.staging):**
```bash
# Application
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Database (Azure PostgreSQL Flexible Server)
DATABASE_HOST=adm-compliance-staging.postgres.database.azure.com
DATABASE_PORT=5432
DATABASE_NAME=adm_compliance
DATABASE_USER=admapp@adm-compliance-staging
DATABASE_PASSWORD=${AZURE_KEY_VAULT_SECRET}
DATABASE_SSL_MODE=require

# Redis (Azure Cache for Redis)
REDIS_URL=rediss://:${REDIS_PASSWORD}@adm-staging-redis.redis.cache.windows.net:6380/0

# Security
JWT_SECRET_KEY=${AZURE_KEY_VAULT_SECRET}
JWT_ALGORITHM=RS256
JWT_EXPIRATION_MINUTES=30

# Frontend
REACT_APP_API_URL=https://api.staging.adm-compliance.gov.au/api
REACT_APP_ENVIRONMENT=staging

# Email (SendGrid)
SMTP_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=${SENDGRID_API_KEY}
EMAIL_FROM=noreply@adm-compliance.gov.au

# File Storage (Azure Blob)
FILE_STORAGE_TYPE=azure_blob
AZURE_STORAGE_ACCOUNT=admcompliancestaging
AZURE_STORAGE_CONTAINER=documents
AZURE_STORAGE_CONNECTION_STRING=${AZURE_KEY_VAULT_SECRET}

# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=${AZURE_KEY_VAULT_SECRET}
```

**Production (.env.production):**
```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (Azure PostgreSQL Flexible Server with HA)
DATABASE_HOST=adm-compliance-prod.postgres.database.azure.com
DATABASE_PORT=5432
DATABASE_NAME=adm_compliance
DATABASE_USER=admapp@adm-compliance-prod
DATABASE_PASSWORD=${AZURE_KEY_VAULT_SECRET}
DATABASE_SSL_MODE=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis (Azure Cache for Redis - Premium with clustering)
REDIS_URL=rediss://:${REDIS_PASSWORD}@adm-prod-redis.redis.cache.windows.net:6380/0

# Security
JWT_SECRET_KEY=${AZURE_KEY_VAULT_SECRET}
JWT_ALGORITHM=RS256
JWT_EXPIRATION_MINUTES=15
CORS_ORIGINS=https://adm-compliance.gov.au

# Frontend
REACT_APP_API_URL=https://api.adm-compliance.gov.au/api
REACT_APP_ENVIRONMENT=production

# Email
SMTP_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=${SENDGRID_API_KEY}
EMAIL_FROM=noreply@adm-compliance.gov.au

# File Storage
FILE_STORAGE_TYPE=azure_blob
AZURE_STORAGE_ACCOUNT=admcomplianceprod
AZURE_STORAGE_CONTAINER=documents
AZURE_STORAGE_CONNECTION_STRING=${AZURE_KEY_VAULT_SECRET}

# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=${AZURE_KEY_VAULT_SECRET}
SENTRY_DSN=${SENTRY_DSN}

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

---

## Local Development Deployment

### Quick Start (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-org/adm-compliance-framework.git
cd adm-compliance-framework

# 2. Run quick start
make quickstart

# This will:
# - Build Docker images
# - Start all services
# - Run database migrations
# - Seed initial data

# 3. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# PgAdmin: http://localhost:5050
```

### Manual Local Setup

```bash
# 1. Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Install frontend dependencies
cd ../frontend
npm install

# 3. Start PostgreSQL (using Docker)
docker run -d \
  --name adm-postgres \
  -e POSTGRES_DB=adm_compliance_dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres123 \
  -p 5432:5432 \
  postgres:15

# 4. Start Redis (using Docker)
docker run -d \
  --name adm-redis \
  -p 6379:6379 \
  redis:7-alpine

# 5. Run database migrations
cd backend
alembic upgrade head

# 6. Seed initial data (optional)
python -m app.utils.seed_data

# 7. Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. Start frontend (in new terminal)
cd frontend
npm start

# 9. Start Celery workers (in new terminal)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

---

## Docker Compose Deployment

### Standard Deployment

```bash
# 1. Clone and navigate to repository
git clone https://github.com/your-org/adm-compliance-framework.git
cd adm-compliance-framework

# 2. Create environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Build images
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Check service status
docker-compose ps

# Expected output:
# NAME                       STATUS              PORTS
# adm-postgres               Up (healthy)        0.0.0.0:5432->5432/tcp
# adm-redis                  Up (healthy)        0.0.0.0:6379->6379/tcp
# adm-backend                Up (healthy)        0.0.0.0:8000->8000/tcp
# adm-frontend               Up (healthy)        0.0.0.0:3000->3000/tcp
# adm-worker                 Up
# adm-pgadmin                Up                  0.0.0.0:5050->80/tcp

# 6. Run database migrations
docker-compose exec backend alembic upgrade head

# 7. Create admin user
docker-compose exec backend python -m app.utils.create_admin_user

# 8. View logs
docker-compose logs -f backend frontend

# 9. Access application
# Open browser to http://localhost:3000
```

### Production-Like Docker Compose

```bash
# Use production compose file with SSL, monitoring, etc.
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# This adds:
# - NGINX reverse proxy with SSL
# - Let's Encrypt certificate management
# - Prometheus monitoring
# - Grafana dashboards
# - Backup containers
```

---

## Azure Production Deployment

### Prerequisites

```bash
# 1. Login to Azure
az login

# 2. Set subscription
az account set --subscription "Your Subscription Name"

# 3. Verify location (must be Australian regions)
az account list-locations --query "[?contains(name, 'australia')]" -o table

# Expected output:
# DisplayName              Name                RegionalDisplayName
# Australia East           australiaeast       (Asia Pacific) Australia East
# Australia Southeast      australiasoutheast  (Asia Pacific) Australia Southeast
```

### Infrastructure Provisioning (Terraform)

```bash
# 1. Navigate to Terraform directory
cd infrastructure/terraform

# 2. Initialize Terraform
terraform init

# 3. Create workspace for environment
terraform workspace new production  # or 'staging'
terraform workspace select production

# 4. Review planned changes
terraform plan -out=tfplan

# Review output carefully:
# - Verify all resources are in australiaeast or australiasoutheast
# - Check resource naming conventions
# - Validate network security groups
# - Confirm database HA settings

# 5. Apply infrastructure changes
terraform apply tfplan

# This will create:
# - Resource Group
# - Virtual Network with subnets
# - AKS cluster (3 nodes minimum)
# - PostgreSQL Flexible Server with HA
# - Azure Cache for Redis (Premium)
# - Azure Container Registry
# - Application Gateway with WAF
# - Azure Key Vault
# - Storage Account with blob containers
# - Log Analytics Workspace
# - Application Insights

# 6. Save outputs
terraform output -json > terraform-outputs.json

# 7. Get AKS credentials
az aks get-credentials \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-aks \
  --admin
```

### Database Setup

```bash
# 1. Connect to PostgreSQL
az postgres flexible-server connect \
  --name adm-compliance-prod-db \
  --resource-group adm-compliance-prod-rg \
  --admin-user admapp \
  --admin-password 'YourSecurePassword123!'

# 2. Create database
CREATE DATABASE adm_compliance;

# 3. Create application user
CREATE USER admapp WITH ENCRYPTED PASSWORD 'YourAppPassword123!';
GRANT ALL PRIVILEGES ON DATABASE adm_compliance TO admapp;

# 4. Enable required extensions
\c adm_compliance
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

# 5. Exit PostgreSQL
\q

# 6. Update connection string in Key Vault
az keyvault secret set \
  --vault-name adm-compliance-prod-kv \
  --name DATABASE-URL \
  --value "postgresql://admapp:YourAppPassword123!@adm-compliance-prod-db.postgres.database.azure.com:5432/adm_compliance?sslmode=require"
```

### Container Registry Setup

```bash
# 1. Login to ACR
az acr login --name admcomplianceprodacr

# 2. Build and push backend image
cd backend
docker build -t admcomplianceprodacr.azurecr.io/adm-backend:1.0.0 .
docker push admcomplianceprodacr.azurecr.io/adm-backend:1.0.0

# 3. Build and push frontend image
cd ../frontend
docker build -t admcomplianceprodacr.azurecr.io/adm-frontend:1.0.0 .
docker push admcomplianceprodacr.azurecr.io/adm-frontend:1.0.0

# 4. Build and push worker image
cd ../backend
docker build -f Dockerfile.worker -t admcomplianceprodacr.azurecr.io/adm-worker:1.0.0 .
docker push admcomplianceprodacr.azurecr.io/adm-worker:1.0.0

# 5. Verify images
az acr repository list --name admcomplianceprodacr -o table
```

### Kubernetes Deployment

```bash
# 1. Create namespace
kubectl create namespace adm-compliance

# 2. Create secrets from Key Vault
kubectl create secret generic adm-secrets \
  --from-literal=database-url=$(az keyvault secret show --vault-name adm-compliance-prod-kv --name DATABASE-URL --query value -o tsv) \
  --from-literal=jwt-secret=$(az keyvault secret show --vault-name adm-compliance-prod-kv --name JWT-SECRET --query value -o tsv) \
  --from-literal=redis-password=$(az keyvault secret show --vault-name adm-compliance-prod-kv --name REDIS-PASSWORD --query value -o tsv) \
  --namespace adm-compliance

# 3. Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/worker-deployment.yaml
kubectl apply -f infrastructure/kubernetes/services.yaml
kubectl apply -f infrastructure/kubernetes/ingress.yaml
kubectl apply -f infrastructure/kubernetes/hpa.yaml

# 4. Verify deployments
kubectl get pods -n adm-compliance

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# adm-backend-7d6f8b9c4-abc12       1/1     Running   0          2m
# adm-backend-7d6f8b9c4-def34       1/1     Running   0          2m
# adm-backend-7d6f8b9c4-ghi56       1/1     Running   0          2m
# adm-frontend-6c5d4a8b2-jkl78      1/1     Running   0          2m
# adm-frontend-6c5d4a8b2-mno90      1/1     Running   0          2m
# adm-worker-5b4c3d2e1-pqr12        1/1     Running   0          2m

# 5. Check services
kubectl get svc -n adm-compliance

# 6. Check ingress
kubectl get ingress -n adm-compliance
```

### Database Migration in Production

```bash
# 1. Get backend pod name
BACKEND_POD=$(kubectl get pods -n adm-compliance -l app=backend -o jsonpath='{.items[0].metadata.name}')

# 2. Run migrations
kubectl exec -it $BACKEND_POD -n adm-compliance -- alembic upgrade head

# 3. Verify migration
kubectl exec -it $BACKEND_POD -n adm-compliance -- alembic current

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# <revision_id> (head)

# 4. Check database version
kubectl exec -it $BACKEND_POD -n adm-compliance -- python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version FROM alembic_version'))
    print(f'Current database version: {result.scalar()}')
"
```

### DNS Configuration

```bash
# 1. Get Application Gateway public IP
APPGW_IP=$(az network public-ip show \
  --resource-group adm-compliance-prod-rg \
  --name adm-appgw-pip \
  --query ipAddress -o tsv)

echo "Application Gateway IP: $APPGW_IP"

# 2. Update DNS records (manual step in your DNS provider)
# Create A records:
# adm-compliance.gov.au → $APPGW_IP
# api.adm-compliance.gov.au → $APPGW_IP
# www.adm-compliance.gov.au → $APPGW_IP

# 3. Verify DNS propagation
nslookup adm-compliance.gov.au
dig adm-compliance.gov.au

# 4. Test SSL certificate
curl -I https://adm-compliance.gov.au
```

### SSL Certificate Setup

```bash
# Option 1: Let's Encrypt with Cert-Manager (Recommended)

# 1. Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 2. Create ClusterIssuer
kubectl apply -f infrastructure/kubernetes/cert-issuer.yaml

# 3. Certificate will be automatically provisioned via ingress annotation
# Check status:
kubectl get certificate -n adm-compliance

# Option 2: Manual Certificate Upload

# 1. Upload certificate to Key Vault
az keyvault certificate import \
  --vault-name adm-compliance-prod-kv \
  --name adm-compliance-ssl-cert \
  --file /path/to/certificate.pfx

# 2. Configure Application Gateway to use certificate
az network application-gateway ssl-cert create \
  --resource-group adm-compliance-prod-rg \
  --gateway-name adm-compliance-appgw \
  --name adm-ssl-cert \
  --key-vault-secret-id $(az keyvault certificate show --vault-name adm-compliance-prod-kv --name adm-compliance-ssl-cert --query sid -o tsv)
```

---

## Database Migration

### Creating New Migrations

```bash
# 1. Make changes to SQLAlchemy models in backend/app/models/

# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Add new field to ADM system"

# 3. Review generated migration in backend/alembic/versions/
# IMPORTANT: Always review auto-generated migrations!

# 4. Edit migration if needed
# - Add data migrations
# - Handle backwards compatibility
# - Add indexes
# - Update constraints

# 5. Test migration on development database
alembic upgrade head

# 6. Test rollback
alembic downgrade -1
alembic upgrade head

# 7. Commit migration file to Git
git add backend/alembic/versions/*.py
git commit -m "Add migration: Add new field to ADM system"
```

### Running Migrations in Production

```bash
# IMPORTANT: Always backup database before migrations!

# 1. Create database backup
az postgres flexible-server backup create \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --backup-name "pre-migration-$(date +%Y%m%d-%H%M%S)"

# 2. Enable maintenance mode (optional but recommended)
kubectl scale deployment adm-backend --replicas=1 -n adm-compliance

# 3. Run migration
BACKEND_POD=$(kubectl get pods -n adm-compliance -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $BACKEND_POD -n adm-compliance -- alembic upgrade head

# 4. Verify migration success
kubectl exec -it $BACKEND_POD -n adm-compliance -- alembic current

# 5. Smoke test application
curl -f https://api.adm-compliance.gov.au/health

# 6. Scale back up
kubectl scale deployment adm-backend --replicas=3 -n adm-compliance

# 7. Monitor for errors
kubectl logs -f -n adm-compliance -l app=backend --tail=100
```

### Migration Rollback

```bash
# If migration causes issues:

# 1. Scale down to single instance
kubectl scale deployment adm-backend --replicas=1 -n adm-compliance

# 2. Rollback migration
BACKEND_POD=$(kubectl get pods -n adm-compliance -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $BACKEND_POD -n adm-compliance -- alembic downgrade -1

# 3. Verify rollback
kubectl exec -it $BACKEND_POD -n adm-compliance -- alembic current

# 4. Restore from backup if needed
az postgres flexible-server restore \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db-restored \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "2024-01-15T10:30:00Z"

# 5. Update connection string to point to restored database
# 6. Scale back up
kubectl scale deployment adm-backend --replicas=3 -n adm-compliance
```

---

## Configuration Management

### Azure Key Vault Integration

```bash
# 1. Store secrets in Key Vault
az keyvault secret set --vault-name adm-compliance-prod-kv --name DATABASE-URL --value "postgresql://..."
az keyvault secret set --vault-name adm-compliance-prod-kv --name JWT-SECRET --value "your-secret-key"
az keyvault secret set --vault-name adm-compliance-prod-kv --name REDIS-PASSWORD --value "your-redis-password"
az keyvault secret set --vault-name adm-compliance-prod-kv --name SENDGRID-API-KEY --value "SG...."

# 2. Grant AKS access to Key Vault (using managed identity)
# Get AKS managed identity
AKS_IDENTITY=$(az aks show --resource-group adm-compliance-prod-rg --name adm-compliance-aks --query identityProfile.kubeletidentity.clientId -o tsv)

# Grant access
az keyvault set-policy \
  --name adm-compliance-prod-kv \
  --object-id $AKS_IDENTITY \
  --secret-permissions get list

# 3. Use CSI Secret Store driver in Kubernetes
kubectl apply -f infrastructure/kubernetes/secret-provider-class.yaml
```

### Environment-Specific Configuration

**config/production.yaml:**
```yaml
application:
  name: ADM Compliance Framework
  version: 1.0.0
  environment: production
  debug: false

database:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 3600

redis:
  max_connections: 50
  socket_timeout: 5

security:
  jwt_expiration_minutes: 15
  refresh_token_expiration_days: 7
  password_min_length: 12
  require_mfa: true

rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst_size: 10

monitoring:
  enable_metrics: true
  enable_tracing: true
  log_level: WARNING
```

---

## Health Checks & Validation

### Automated Health Checks

```bash
# 1. Backend health
curl -f https://api.adm-compliance.gov.au/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "checks": {
#     "database": "ok",
#     "redis": "ok",
#     "storage": "ok"
#   },
#   "timestamp": "2024-01-15T10:30:00Z"
# }

# 2. Frontend health
curl -f https://adm-compliance.gov.au

# 3. Database connectivity
kubectl exec -it $BACKEND_POD -n adm-compliance -- python -c "
from app.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database OK' if result.scalar() == 1 else 'Database FAIL')
"

# 4. Redis connectivity
kubectl exec -it $BACKEND_POD -n adm-compliance -- python -c "
import redis
from app.config import settings
r = redis.from_url(settings.REDIS_URL)
print('Redis OK' if r.ping() else 'Redis FAIL')
"

# 5. Check all pods
kubectl get pods -n adm-compliance

# All pods should show:
# - READY: 1/1
# - STATUS: Running
# - RESTARTS: Low number (< 5)
```

### Smoke Tests

```bash
# Run post-deployment smoke tests
cd tests
./smoke-tests.sh production

# Tests include:
# - Login flow
# - Create ADM system
# - Access dashboard
# - Generate report
# - Submit individual request
# - API endpoints
```

### Performance Validation

```bash
# 1. Load test with k6
k6 run tests/load-test.js --vus 100 --duration 5m

# 2. Expected metrics:
# - http_req_duration: p95 < 500ms
# - http_req_failed: < 1%
# - http_reqs: > 1000/s

# 3. Monitor resource usage during load test
kubectl top pods -n adm-compliance
kubectl top nodes
```

---

## Rollback Procedures

### Application Rollback

```bash
# 1. Identify previous working version
kubectl rollout history deployment adm-backend -n adm-compliance

# 2. Rollback to previous version
kubectl rollout undo deployment adm-backend -n adm-compliance

# 3. Rollback to specific version
kubectl rollout undo deployment adm-backend --to-revision=5 -n adm-compliance

# 4. Monitor rollback
kubectl rollout status deployment adm-backend -n adm-compliance

# 5. Verify health
curl -f https://api.adm-compliance.gov.au/health

# 6. Rollback frontend
kubectl rollout undo deployment adm-frontend -n adm-compliance
```

### Database Rollback

```bash
# 1. Rollback migration (see Database Migration section)

# 2. Point-in-time restore (if needed)
az postgres flexible-server restore \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db-restored \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "2024-01-15T09:00:00Z"

# 3. Update connection string
# 4. Restart application pods
kubectl rollout restart deployment adm-backend -n adm-compliance
```

### Complete Environment Rollback

```bash
# Use Terraform to rollback infrastructure changes

# 1. Navigate to Terraform directory
cd infrastructure/terraform

# 2. Checkout previous Terraform state
git checkout <previous-commit> -- .

# 3. Review changes
terraform plan

# 4. Apply rollback
terraform apply

# 5. Update Kubernetes deployments to match infrastructure
kubectl apply -f infrastructure/kubernetes/
```

---

## Troubleshooting

### Common Issues

**Issue: Pods stuck in Pending state**
```bash
# Check events
kubectl describe pod <pod-name> -n adm-compliance

# Common causes:
# - Insufficient resources → Scale up node pool
# - Image pull errors → Check ACR credentials
# - PVC binding issues → Check storage class
```

**Issue: Database connection errors**
```bash
# Check connectivity
kubectl exec -it $BACKEND_POD -n adm-compliance -- ping adm-compliance-prod-db.postgres.database.azure.com

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db

# Add AKS subnet to firewall
az postgres flexible-server firewall-rule create \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --rule-name allow-aks \
  --start-ip-address <aks-subnet-start> \
  --end-ip-address <aks-subnet-end>
```

**Issue: SSL certificate errors**
```bash
# Check certificate status
kubectl describe certificate adm-compliance-cert -n adm-compliance

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Manually trigger certificate renewal
kubectl delete certificate adm-compliance-cert -n adm-compliance
kubectl apply -f infrastructure/kubernetes/ingress.yaml
```

**Issue: High memory usage**
```bash
# Check memory usage
kubectl top pods -n adm-compliance

# Increase memory limits
kubectl set resources deployment adm-backend --limits=memory=4Gi -n adm-compliance

# Check for memory leaks
kubectl exec -it $BACKEND_POD -n adm-compliance -- python -m memory_profiler app/main.py
```

### Logging and Debugging

```bash
# View application logs
kubectl logs -f deployment/adm-backend -n adm-compliance

# View last 1000 lines
kubectl logs --tail=1000 deployment/adm-backend -n adm-compliance

# Filter logs
kubectl logs deployment/adm-backend -n adm-compliance | grep ERROR

# View Azure Application Insights
az monitor app-insights query \
  --app adm-compliance-prod-appinsights \
  --analytics-query "traces | where severityLevel >= 3 | take 100"
```

---

## Post-Deployment Tasks

### Post-Deployment Checklist

- [ ] Verify all pods running and healthy
- [ ] Confirm database migrations applied
- [ ] Test user authentication
- [ ] Validate SSL certificates
- [ ] Check monitoring dashboards
- [ ] Review error logs (should be minimal)
- [ ] Test critical user flows
- [ ] Verify backup jobs scheduled
- [ ] Update deployment documentation
- [ ] Notify stakeholders of deployment
- [ ] Monitor for 24 hours
- [ ] Schedule post-deployment review

### Monitoring Setup

```bash
# 1. Verify Application Insights data
az monitor app-insights metrics show \
  --app adm-compliance-prod-appinsights \
  --metric requests/count \
  --interval PT1H

# 2. Create alerts
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group adm-compliance-prod-rg \
  --scopes /subscriptions/.../adm-compliance-aks \
  --condition "avg failed_requests > 10" \
  --window-size 5m \
  --evaluation-frequency 1m

# 3. Configure Azure Monitor dashboards
az portal dashboard create \
  --name adm-compliance-dashboard \
  --input-path infrastructure/monitoring/dashboard.json
```

### Backup Verification

```bash
# 1. Verify automatic backups enabled
az postgres flexible-server show \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --query backup

# 2. Test backup restore (to separate server)
az postgres flexible-server restore \
  --resource-group adm-compliance-test-rg \
  --name adm-compliance-backup-test \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "2024-01-15T10:00:00Z"

# 3. Verify restored data
# Connect and run sample queries
```

---

## Appendix

### Deployment Checklist Template

```markdown
## Deployment: [Version] to [Environment]
**Date**: YYYY-MM-DD
**Deployer**: [Name]
**Approver**: [Name]

### Pre-Deployment
- [ ] Change request approved
- [ ] Code reviewed and merged
- [ ] All tests passing
- [ ] Database backup created
- [ ] Rollback plan documented
- [ ] Stakeholders notified

### Deployment
- [ ] Infrastructure provisioned
- [ ] Secrets configured
- [ ] Docker images built and pushed
- [ ] Kubernetes deployments updated
- [ ] Database migrations run
- [ ] DNS updated
- [ ] SSL certificates validated

### Post-Deployment
- [ ] Health checks passed
- [ ] Smoke tests passed
- [ ] Monitoring configured
- [ ] Logs reviewed
- [ ] Performance validated
- [ ] Backup verified
- [ ] Documentation updated

### Sign-Off
- [ ] Deployment successful
- [ ] Issues: [None / List issues]
- [ ] Rollback required: [Yes / No]
```

### Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| **Technical Lead** | [Name] | [Phone] | [Email] |
| **DevOps Engineer** | [Name] | [Phone] | [Email] |
| **Database Admin** | [Name] | [Phone] | [Email] |
| **Security Officer** | [Name] | [Phone] | [Email] |
| **Azure Support** | Microsoft | 1800 XXX XXX | azure-support@microsoft.com |

### Useful Commands Reference

```bash
# Quick status check
make health

# View all services
kubectl get all -n adm-compliance

# Restart all pods
kubectl rollout restart deployment -n adm-compliance

# Scale deployment
kubectl scale deployment adm-backend --replicas=5 -n adm-compliance

# Port forward for debugging
kubectl port-forward svc/adm-backend 8000:8000 -n adm-compliance

# Execute command in pod
kubectl exec -it <pod-name> -n adm-compliance -- /bin/bash

# Copy files from pod
kubectl cp adm-compliance/<pod-name>:/app/logs/app.log ./app.log
```

---

**Document Version**: 1.0.0
**Last Reviewed**: 2024-01-XX
**Next Review**: Quarterly
**Owner**: DevOps Team
