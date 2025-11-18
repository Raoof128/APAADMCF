# Backup and Disaster Recovery Plan

**Australian Privacy Act ADM Compliance Framework**

Version: 1.0.0
Last Updated: 2024-01-XX

---

## Table of Contents

- [Overview](#overview)
- [Recovery Objectives](#recovery-objectives)
- [Backup Strategy](#backup-strategy)
- [Database Backup](#database-backup)
- [Application Backup](#application-backup)
- [Infrastructure Backup](#infrastructure-backup)
- [Backup Verification](#backup-verification)
- [Disaster Recovery Procedures](#disaster-recovery-procedures)
- [Failover Procedures](#failover-procedures)
- [Recovery Testing](#recovery-testing)
- [Monitoring and Alerts](#monitoring-and-alerts)

---

## Overview

This document outlines the backup and disaster recovery (DR) strategy for the ADM Compliance Framework, ensuring business continuity and data protection in compliance with Australian Privacy Act requirements.

### Scope

**Systems Covered:**
- PostgreSQL Database (primary data store)
- Azure Blob Storage (documents, reports)
- Application configuration and secrets
- Infrastructure as Code (Terraform state)
- Source code repositories
- Kubernetes cluster state

**Compliance Requirements:**
- Privacy Act 1988 - APP 11 (Security of personal information)
- Retain audit logs for 7 years minimum
- Geographic data residency (Australia only)
- Encryption at rest and in transit
- Immutable backup retention for compliance data

---

## Recovery Objectives

### Service Level Objectives (SLOs)

| Scenario | RTO (Recovery Time) | RPO (Data Loss) | Priority |
|----------|---------------------|-----------------|----------|
| **Individual Pod Failure** | < 1 minute | 0 (no data loss) | Critical |
| **Node Failure** | < 5 minutes | 0 (no data loss) | Critical |
| **Availability Zone Failure** | < 15 minutes | < 5 minutes | Critical |
| **Database Corruption** | < 2 hours | < 15 minutes | High |
| **Application Bug (Rollback)** | < 30 minutes | 0 (rollback only) | High |
| **Regional Disaster** | < 4 hours | < 1 hour | High |
| **Complete Data Center Loss** | < 8 hours | < 1 hour | Medium |
| **Ransomware Attack** | < 12 hours | < 1 day | Medium |
| **Accidental Data Deletion** | < 1 hour | 0 (point-in-time) | High |

### Business Impact Analysis

| System Component | Criticality | Impact of 1 Hour Downtime | Impact of 1 Day Downtime |
|------------------|-------------|---------------------------|--------------------------|
| **Database** | Critical | Cannot process requests, data access blocked | Complete service outage, compliance breach |
| **Backend API** | Critical | All functionality unavailable | Service unusable, SLA breach |
| **Frontend** | High | User interface unavailable | Users cannot access system |
| **Workers (Celery)** | Medium | Delayed reports, emails | Backlog of async tasks |
| **File Storage** | Medium | Cannot access reports/documents | Historical data unavailable |
| **Cache (Redis)** | Low | Slower performance | Degraded performance |

---

## Backup Strategy

### Backup Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Backup Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Production (Australia East)                                │
│  ┌────────────────────┐          ┌──────────────────────┐  │
│  │  PostgreSQL        │          │  Blob Storage        │  │
│  │  Primary Database  │          │  (Documents/Reports) │  │
│  └─────────┬──────────┘          └───────────┬──────────┘  │
│            │                                  │             │
│            │ Continuous WAL                   │ GRS         │
│            │ Streaming                        │ Replication │
│            ↓                                  ↓             │
│  ┌────────────────────┐          ┌──────────────────────┐  │
│  │  Read Replica      │          │  Storage Account     │  │
│  │  (Hot Standby)     │          │  (Geo-Redundant)     │  │
│  └─────────┬──────────┘          └───────────┬──────────┘  │
│            │                                  │             │
│            │ Daily Snapshots                  │             │
│            │ Transaction Logs (15 min)        │             │
│            ↓                                  ↓             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Azure Backup Vault (Australia East)              │    │
│  │  - Daily Full Backups (30 days)                   │    │
│  │  - Transaction Logs (30 days)                     │    │
│  │  - Monthly Backups (7 years for audit logs)       │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                     │
│                       │ Cross-Region Replication            │
│                       ↓                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Azure Backup Vault (Australia Southeast)         │    │
│  │  - Geo-Redundant Copy                             │    │
│  │  - Immutable for 90 days (ransomware protection)  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  DR Region (Australia Southeast)                            │
│  ┌────────────────────┐          ┌──────────────────────┐  │
│  │  PostgreSQL        │          │  Blob Storage        │  │
│  │  Geo-Replica (RO)  │          │  Secondary Region    │  │
│  └────────────────────┘          └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Backup Types

**Full Backup:**
- Frequency: Daily at 02:00 AEST
- Retention: 30 days (standard data), 7 years (audit logs)
- Method: PostgreSQL pg_basebackup + Azure Backup
- Storage: Azure Backup Vault (GRS)

**Incremental Backup:**
- Frequency: Every 6 hours
- Retention: 7 days
- Method: Differential backup (changed data only)
- Storage: Azure Backup Vault

**Transaction Log Backup:**
- Frequency: Every 15 minutes
- Retention: 30 days
- Method: PostgreSQL WAL archiving
- Storage: Azure Blob Storage (GRS)

**Continuous Replication:**
- Method: PostgreSQL streaming replication
- Lag: < 30 seconds
- Destination: Read replica (Australia East), Geo-replica (Australia Southeast)

### Retention Policy

| Data Type | Retention Period | Backup Frequency | Storage Tier |
|-----------|------------------|------------------|--------------|
| **Database - Standard** | 30 days | Daily + Transaction logs | Hot |
| **Database - Audit Logs** | 7 years | Monthly (locked) | Archive |
| **Application Logs** | 90 days | Daily | Cool |
| **File Storage (Reports)** | 7 years | Continuous (GRS) | Archive |
| **Infrastructure Config** | Indefinite (versioned) | On change | Hot |
| **Application Code** | Indefinite (Git) | On commit | N/A |

---

## Database Backup

### Automated Database Backup

**Azure PostgreSQL Flexible Server Backup:**

```bash
# 1. Enable automated backups (configured in Terraform)
az postgres flexible-server update \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --backup-retention 30 \
  --geo-redundant-backup Enabled

# 2. Verify backup configuration
az postgres flexible-server show \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --query '{backupRetentionDays:backup.backupRetentionDays, geoRedundantBackup:backup.geoRedundantBackup}'

# Expected output:
# {
#   "backupRetentionDays": 30,
#   "geoRedundantBackup": "Enabled"
# }

# 3. List available backups
az postgres flexible-server backup list \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --output table

# 4. View backup details
az postgres flexible-server backup show \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --backup-name <backup-name>
```

### Manual Database Backup

**On-Demand Backup (Pre-Maintenance):**

```bash
# 1. Create named backup
az postgres flexible-server backup create \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db \
  --backup-name "manual-backup-$(date +%Y%m%d-%H%M%S)"

# 2. Export logical backup using pg_dump
# Get backend pod
BACKEND_POD=$(kubectl get pods -n adm-compliance -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Create backup directory
kubectl exec -it $BACKEND_POD -n adm-compliance -- mkdir -p /tmp/backups

# Run pg_dump
kubectl exec -it $BACKEND_POD -n adm-compliance -- pg_dump \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -F c \
  -f "/tmp/backups/adm_compliance_$(date +%Y%m%d_%H%M%S).backup"

# 3. Copy backup locally
kubectl cp \
  adm-compliance/$BACKEND_POD:/tmp/backups/adm_compliance_$(date +%Y%m%d_%H%M%S).backup \
  ./backups/

# 4. Upload to Azure Blob Storage
az storage blob upload \
  --account-name admcomplianceprodbackup \
  --container-name database-backups \
  --name "manual/adm_compliance_$(date +%Y%m%d_%H%M%S).backup" \
  --file "./backups/adm_compliance_$(date +%Y%m%d_%H%M%S).backup" \
  --tier Archive

# 5. Verify upload
az storage blob list \
  --account-name admcomplianceprodbackup \
  --container-name database-backups \
  --prefix manual/ \
  --output table
```

### Database Restore Procedures

**Point-in-Time Restore (PITR):**

```bash
# 1. Identify restore point
# List recent backups
az postgres flexible-server backup list \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db

# 2. Restore to new server
az postgres flexible-server restore \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-restored-db \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "2024-01-15T10:30:00Z"

# 3. Wait for restore completion
az postgres flexible-server wait \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-restored-db \
  --exists

# 4. Verify restored data
# Connect and run validation queries
az postgres flexible-server connect \
  --name adm-compliance-restored-db \
  --admin-user admapp

# 5. Update application connection string
kubectl set env deployment/adm-backend \
  DATABASE_URL="postgresql://admapp@adm-compliance-restored-db.postgres.database.azure.com/adm_compliance" \
  -n adm-compliance

# 6. Restart application
kubectl rollout restart deployment/adm-backend -n adm-compliance
```

**Full Database Restore from pg_dump:**

```bash
# 1. Download backup from Azure Blob Storage
az storage blob download \
  --account-name admcomplianceprodbackup \
  --container-name database-backups \
  --name "manual/adm_compliance_20240115_103000.backup" \
  --file "./restore/adm_compliance.backup"

# 2. Drop existing database (DESTRUCTIVE - production warning!)
# Only do this in DR scenario after confirming with stakeholders
kubectl exec -it $BACKEND_POD -n adm-compliance -- psql \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U postgres \
  -c "DROP DATABASE adm_compliance;"

# 3. Create new database
kubectl exec -it $BACKEND_POD -n adm-compliance -- psql \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U postgres \
  -c "CREATE DATABASE adm_compliance OWNER admapp;"

# 4. Restore from backup
kubectl cp ./restore/adm_compliance.backup adm-compliance/$BACKEND_POD:/tmp/
kubectl exec -it $BACKEND_POD -n adm-compliance -- pg_restore \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -F c \
  -v \
  /tmp/adm_compliance.backup

# 5. Verify restore
kubectl exec -it $BACKEND_POD -n adm-compliance -- psql \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -c "SELECT COUNT(*) FROM adm_systems;"

# 6. Restart application
kubectl rollout restart deployment -n adm-compliance
```

### Transaction Log Archiving

**Configure WAL Archiving:**

```bash
# Already configured in PostgreSQL Flexible Server by default
# Verify WAL archiving status
az postgres flexible-server parameter show \
  --resource-group adm-compliance-prod-rg \
  --server-name adm-compliance-prod-db \
  --name archive_mode

# Expected: archive_mode = on

# WAL files are automatically archived to Azure Blob Storage
# Retention: 30 days (configurable)
```

---

## Application Backup

### Container Image Backup

```bash
# 1. Images are stored in Azure Container Registry with geo-replication
az acr replication list \
  --registry admcomplianceprodacr \
  --output table

# Expected output:
# NAME                 LOCATION            PROVISIONING STATE
# admcomplianceprodacr  australiaeast       Succeeded
# admcomplianceprodacr  australiasoutheast  Succeeded

# 2. Enable immutable tags (prevent accidental deletion)
az acr repository update \
  --name admcomplianceprodacr \
  --repository adm-backend \
  --write-enabled false \
  --delete-enabled false

# 3. Export image to tar (for offline backup)
docker pull admcomplianceprodacr.azurecr.io/adm-backend:1.0.0
docker save admcomplianceprodacr.azurecr.io/adm-backend:1.0.0 -o adm-backend-1.0.0.tar

# 4. Upload to archive storage
az storage blob upload \
  --account-name admcomplianceprodbackup \
  --container-name container-images \
  --name "adm-backend-1.0.0.tar" \
  --file adm-backend-1.0.0.tar \
  --tier Archive
```

### Configuration Backup

```bash
# 1. Export Kubernetes ConfigMaps
kubectl get configmap -n adm-compliance -o yaml > backups/configmaps-$(date +%Y%m%d).yaml

# 2. Export Kubernetes Secrets (encrypted)
# Never store unencrypted secrets!
kubectl get secret -n adm-compliance -o yaml | \
  gpg --encrypt --recipient ops@adm-compliance.gov.au > backups/secrets-$(date +%Y%m%d).yaml.gpg

# 3. Export all Kubernetes resources
kubectl get all -n adm-compliance -o yaml > backups/k8s-resources-$(date +%Y%m%d).yaml

# 4. Backup Azure Key Vault secrets
az keyvault backup start \
  --vault-name adm-compliance-prod-kv \
  --storage-account-name admcomplianceprodbackup \
  --storage-container-name key-vault-backup \
  --blob-name "keyvault-backup-$(date +%Y%m%d)"

# 5. Upload to secure storage
az storage blob upload-batch \
  --account-name admcomplianceprodbackup \
  --destination config-backups \
  --source ./backups/ \
  --pattern "*.yaml"
```

### Application Data Backup (Blob Storage)

```bash
# 1. Verify geo-redundant storage enabled
az storage account show \
  --name admcomplianceprod \
  --query '{sku:sku.name, location:primaryLocation, secondaryLocation:secondaryLocation}'

# Expected output:
# {
#   "sku": "Standard_GRS",
#   "location": "australiaeast",
#   "secondaryLocation": "australiasoutheast"
# }

# 2. Enable blob versioning (immutable backups)
az storage account blob-service-properties update \
  --account-name admcomplianceprod \
  --enable-versioning true

# 3. Enable soft delete (30 days)
az storage account blob-service-properties update \
  --account-name admcomplianceprod \
  --enable-delete-retention true \
  --delete-retention-days 30

# 4. Create manual snapshot of critical container
az storage blob snapshot \
  --account-name admcomplianceprod \
  --container-name documents \
  --name important-file.pdf

# 5. Export critical files for offline storage
az storage blob download-batch \
  --account-name admcomplianceprod \
  --source documents \
  --destination ./offline-backup/ \
  --pattern "audit-reports/*"
```

---

## Infrastructure Backup

### Terraform State Backup

```bash
# 1. Terraform state is stored in Azure Storage with versioning
az storage container show \
  --account-name admcompliancetfstate \
  --name terraform-state \
  --query '{versioning:properties.hasImmutabilityPolicy}'

# 2. Download current state
az storage blob download \
  --account-name admcompliancetfstate \
  --container-name terraform-state \
  --name production/terraform.tfstate \
  --file ./backups/terraform-state-$(date +%Y%m%d).json

# 3. List state versions
az storage blob list \
  --account-name admcompliancetfstate \
  --container-name terraform-state \
  --prefix production/ \
  --include-versions \
  --output table

# 4. Restore previous state version if needed
az storage blob download \
  --account-name admcompliancetfstate \
  --container-name terraform-state \
  --name production/terraform.tfstate \
  --version-id <version-id> \
  --file ./terraform.tfstate.restore
```

### Infrastructure as Code Backup

```bash
# All IaC is version controlled in Git
# Additional backup to Azure Blob Storage

# 1. Create tarball of infrastructure directory
tar -czf infrastructure-backup-$(date +%Y%m%d).tar.gz infrastructure/

# 2. Upload to Azure Storage
az storage blob upload \
  --account-name admcomplianceprodbackup \
  --container-name infrastructure-backups \
  --name "infrastructure-backup-$(date +%Y%m%d).tar.gz" \
  --file infrastructure-backup-$(date +%Y%m%d).tar.gz \
  --tier Archive

# 3. Verify upload
az storage blob list \
  --account-name admcomplianceprodbackup \
  --container-name infrastructure-backups \
  --output table
```

---

## Backup Verification

### Automated Backup Testing

**Daily Backup Verification Script:**

```bash
#!/bin/bash
# scripts/verify-backups.sh

set -euo pipefail

RESOURCE_GROUP="adm-compliance-prod-rg"
DB_SERVER="adm-compliance-prod-db"
STORAGE_ACCOUNT="admcomplianceprodbackup"

echo "=== ADM Compliance Framework - Backup Verification ==="
echo "Date: $(date)"
echo ""

# 1. Verify database backup
echo "1. Checking database backups..."
LATEST_BACKUP=$(az postgres flexible-server backup list \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --query "[0].name" -o tsv)

if [ -z "$LATEST_BACKUP" ]; then
  echo "❌ ERROR: No database backups found!"
  exit 1
else
  echo "✅ Latest database backup: $LATEST_BACKUP"
fi

# 2. Verify backup age (should be < 24 hours)
BACKUP_TIME=$(az postgres flexible-server backup show \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --backup-name $LATEST_BACKUP \
  --query backupTime -o tsv)

BACKUP_AGE=$(($(date +%s) - $(date -d "$BACKUP_TIME" +%s)))
HOURS=$((BACKUP_AGE / 3600))

if [ $HOURS -gt 24 ]; then
  echo "❌ ERROR: Latest backup is $HOURS hours old (should be < 24)"
  exit 1
else
  echo "✅ Backup age: $HOURS hours"
fi

# 3. Verify blob storage replication
echo ""
echo "2. Checking blob storage geo-replication..."
REPLICATION_STATUS=$(az storage account show \
  --name $STORAGE_ACCOUNT \
  --query statusOfSecondary -o tsv)

if [ "$REPLICATION_STATUS" != "available" ]; then
  echo "❌ ERROR: Geo-replication not available: $REPLICATION_STATUS"
  exit 1
else
  echo "✅ Geo-replication status: available"
fi

# 4. Verify recent blob uploads
echo ""
echo "3. Checking recent file backups..."
RECENT_BLOBS=$(az storage blob list \
  --account-name $STORAGE_ACCOUNT \
  --container-name documents \
  --num-results 1 \
  --query "[0].properties.lastModified" -o tsv)

if [ -z "$RECENT_BLOBS" ]; then
  echo "⚠️  WARNING: No recent blob uploads found"
else
  echo "✅ Latest blob upload: $RECENT_BLOBS"
fi

# 5. Test restore capability (to test server)
echo ""
echo "4. Testing restore capability..."
# This creates a test restore server (cleaned up after verification)
# Only run in non-production hours to avoid cost

echo "✅ All backup verifications passed!"
echo ""
echo "=== Backup Verification Complete ==="
```

**Schedule automated verification:**

```bash
# Add to crontab
crontab -e

# Run daily at 03:00 AEST
0 3 * * * /home/ops/scripts/verify-backups.sh >> /var/log/backup-verification.log 2>&1
```

### Manual Restore Testing

**Quarterly Restore Test (Required for Compliance):**

```bash
# 1. Schedule restore test (off-hours)
# Document: tests/DR_TEST_PLAN.md

# 2. Create test environment
az group create \
  --name adm-compliance-dr-test-rg \
  --location australiasoutheast

# 3. Restore database to test server
az postgres flexible-server restore \
  --resource-group adm-compliance-dr-test-rg \
  --name adm-compliance-test-restored \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ')"

# 4. Deploy test application pointing to restored database
# (use separate Kubernetes namespace or cluster)

# 5. Run validation tests
cd tests
./validate-restored-data.sh

# Expected checks:
# - Row counts match source
# - Critical records present
# - Data integrity (checksums)
# - Foreign key constraints valid
# - Application can read/write

# 6. Document results in DR test log

# 7. Clean up test environment
az group delete --name adm-compliance-dr-test-rg --yes --no-wait
```

---

## Disaster Recovery Procedures

### Scenario 1: Database Corruption

**Symptoms:**
- Database errors in application logs
- Data inconsistency
- Corrupted indexes or tables

**Recovery Steps:**

```bash
# 1. Assess damage
kubectl exec -it $BACKEND_POD -n adm-compliance -- psql \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -c "SELECT pg_database_size('adm_compliance');"

# 2. Stop write traffic (enable read-only mode)
kubectl scale deployment adm-backend --replicas=0 -n adm-compliance

# 3. Attempt repair
kubectl exec -it $BACKEND_POD -n adm-compliance -- psql \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -c "REINDEX DATABASE adm_compliance;"

# 4. If repair fails, restore from backup
# See "Database Restore Procedures" section

# 5. Verify data integrity
./scripts/verify-database-integrity.sh

# 6. Resume write traffic
kubectl scale deployment adm-backend --replicas=3 -n adm-compliance
```

### Scenario 2: Regional Failure (Australia East Down)

**Recovery Steps:**

```bash
# 1. Confirm regional outage
# Check Azure status: https://status.azure.com/

# 2. Promote geo-replica to primary (Australia Southeast)
az postgres flexible-server geo-restore \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-prod-db-failover \
  --source-server adm-compliance-prod-db \
  --location australiasoutheast

# 3. Update DNS to point to DR region
# Update A records:
# adm-compliance.gov.au → <DR-AppGateway-IP>
# api.adm-compliance.gov.au → <DR-AppGateway-IP>

# 4. Deploy application to DR AKS cluster
kubectl config use-context adm-compliance-dr-aks
kubectl apply -f infrastructure/kubernetes/ -n adm-compliance

# 5. Update database connection strings
kubectl set env deployment/adm-backend \
  DATABASE_URL="postgresql://admapp@adm-compliance-prod-db-failover.postgres.database.azure.com/adm_compliance" \
  -n adm-compliance

# 6. Verify application health
curl -f https://api.adm-compliance.gov.au/health

# 7. Notify stakeholders of failover

# 8. Monitor for primary region recovery
```

### Scenario 3: Ransomware Attack

**Detection:**
- Unusual file encryption activity
- Mass file deletions
- Suspicious authentication
- Alert from Azure Defender

**Recovery Steps:**

```bash
# 1. IMMEDIATE: Isolate affected systems
# Disconnect from network
kubectl scale deployment --all --replicas=0 -n adm-compliance

# 2. Preserve evidence (for investigation)
# Take snapshots of affected VMs/disks

# 3. Assess impact
# Identify compromised data
# Check backup integrity

# 4. Restore from immutable backups
# Use backups from BEFORE attack date

# 5. Restore database from immutable backup
az postgres flexible-server restore \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-clean-db \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "<PRE-ATTACK-TIMESTAMP>"

# 6. Restore blob storage from soft-deleted or versioned blobs
az storage blob list \
  --account-name admcomplianceprod \
  --container-name documents \
  --include-deleted \
  --output table

az storage blob undelete \
  --account-name admcomplianceprod \
  --container-name documents \
  --name <deleted-blob>

# 7. Rebuild infrastructure from IaC
cd infrastructure/terraform
terraform destroy  # Remove compromised infrastructure
terraform apply    # Rebuild from clean state

# 8. Redeploy application with updated security
# - Rotate all secrets
# - Update firewall rules
# - Enable additional monitoring

# 9. Conduct security audit
# - Review access logs
# - Identify attack vector
# - Implement additional controls

# 10. Notify authorities and affected parties
# - Australian Cyber Security Centre (ACSC)
# - Office of the Australian Information Commissioner (OAIC)
# - Affected individuals (if personal data compromised)
```

### Scenario 4: Accidental Data Deletion

**Recovery Steps:**

```bash
# 1. Identify what was deleted and when
# Check audit logs
kubectl exec -it $BACKEND_POD -n adm-compliance -- psql \
  -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -c "SELECT * FROM audit_logs WHERE action LIKE '%DELETE%' ORDER BY timestamp DESC LIMIT 100;"

# 2. For soft-deleted blobs, undelete
az storage blob undelete \
  --account-name admcomplianceprod \
  --container-name documents \
  --name <deleted-blob-name>

# 3. For database records, restore from PITR
# Option A: Restore entire database to point before deletion
# Option B: Restore to separate server and copy specific records

# Restore to temporary server
az postgres flexible-server restore \
  --resource-group adm-compliance-temp-rg \
  --name adm-compliance-temp-restored \
  --source-server adm-compliance-prod-db \
  --restore-point-in-time "<TIMESTAMP-BEFORE-DELETION>"

# Copy specific data
pg_dump -h adm-compliance-temp-restored.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance \
  -t specific_table \
  --data-only | \
  psql -h adm-compliance-prod-db.postgres.database.azure.com \
  -U admapp \
  -d adm_compliance

# 4. Verify restoration
# Run validation queries

# 5. Clean up temporary resources
az group delete --name adm-compliance-temp-rg --yes
```

---

## Failover Procedures

### Automatic Failover (Pod/Node Failure)

**Kubernetes automatically handles:**
- Pod crashes → New pod started immediately
- Node failure → Pods rescheduled to healthy nodes
- No manual intervention required

**Monitoring:**

```bash
# Watch for pod events
kubectl get events -n adm-compliance --watch

# Check pod restarts
kubectl get pods -n adm-compliance -o custom-columns=NAME:.metadata.name,RESTARTS:.status.containerStatuses[0].restartCount
```

### Manual Failover (Planned Maintenance)

**Database Failover:**

```bash
# 1. Announce maintenance window
# 2. Enable read-only mode

kubectl set env deployment/adm-backend READ_ONLY_MODE=true -n adm-compliance

# 3. Promote read replica
az postgres flexible-server replica promote \
  --resource-group adm-compliance-prod-rg \
  --name adm-compliance-read-replica

# 4. Update connection string
kubectl set env deployment/adm-backend \
  DATABASE_URL="<new-primary-connection-string>" \
  -n adm-compliance

# 5. Disable read-only mode
kubectl set env deployment/adm-backend READ_ONLY_MODE=false -n adm-compliance

# 6. Verify write operations
curl -X POST https://api.adm-compliance.gov.au/api/test-write

# 7. Recreate read replica from new primary
az postgres flexible-server replica create \
  --resource-group adm-compliance-prod-rg \
  --source-server adm-compliance-read-replica \
  --name adm-compliance-new-replica
```

---

## Recovery Testing

### Monthly Recovery Tests

**Test Schedule:**

| Week | Test Type | Duration | Systems |
|------|-----------|----------|---------|
| **Week 1** | Database PITR | 30 min | PostgreSQL |
| **Week 2** | Blob Storage Restore | 15 min | Azure Storage |
| **Week 3** | Application Rollback | 20 min | Kubernetes |
| **Week 4** | Config Restore | 15 min | ConfigMaps, Secrets |

**Test Checklist Template:**

```markdown
## Recovery Test - [Test Type] - [Date]

**Tester:** [Name]
**Environment:** [Staging/Production-Like]
**Duration:** [Planned] vs [Actual]

### Pre-Test
- [ ] Backup verified available
- [ ] Test environment prepared
- [ ] Rollback plan documented
- [ ] Stakeholders notified

### Test Execution
- [ ] Backup restored successfully
- [ ] Data integrity verified
- [ ] Application connectivity confirmed
- [ ] Performance acceptable

### Post-Test
- [ ] Test environment cleaned up
- [ ] Results documented
- [ ] Issues identified and tracked
- [ ] RTO/RPO measured
- [ ] Lessons learned captured

### Results
- **Success:** [Yes/No]
- **RTO Target:** [X hours] | **Actual:** [Y hours]
- **RPO Target:** [X min] | **Actual:** [Y min]
- **Issues:** [None / List issues]

### Sign-Off
- [ ] Test completed successfully
- [ ] Report filed
- [ ] Next test scheduled
```

### Annual Full DR Drill

**Comprehensive DR Exercise (Once per year):**

```bash
# Simulate complete regional failure
# Test full failover to DR region

# 1. Schedule DR drill (announce 2 weeks in advance)
# 2. Assemble DR team
# 3. Execute full failover procedure
# 4. Run production-like workload on DR environment
# 5. Measure all KPIs
# 6. Document all steps and timings
# 7. Conduct post-mortem review
# 8. Update DR procedures based on findings
```

---

## Monitoring and Alerts

### Backup Monitoring

**Azure Monitor Alerts:**

```bash
# 1. Alert on backup failure
az monitor metrics alert create \
  --name backup-failure-alert \
  --resource-group adm-compliance-prod-rg \
  --scopes /subscriptions/.../adm-compliance-prod-db \
  --condition "count backup_failures > 0" \
  --window-size 1h \
  --evaluation-frequency 15m \
  --action-group backup-alerts

# 2. Alert on backup age (no backup in 25 hours)
az monitor metrics alert create \
  --name backup-age-alert \
  --resource-group adm-compliance-prod-rg \
  --scopes /subscriptions/.../adm-compliance-prod-db \
  --condition "max backup_age_hours > 25" \
  --window-size 1h \
  --evaluation-frequency 1h \
  --action-group backup-alerts

# 3. Alert on replication lag
az monitor metrics alert create \
  --name replication-lag-alert \
  --resource-group adm-compliance-prod-rg \
  --scopes /subscriptions/.../adm-compliance-prod-db \
  --condition "max replication_lag_seconds > 300" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group backup-alerts
```

### Dashboard Metrics

**Key Metrics to Monitor:**

1. **Backup Health**
   - Last successful backup timestamp
   - Backup size trend
   - Backup duration
   - Failed backup count

2. **Replication Health**
   - Replication lag (seconds)
   - Replication status
   - WAL file archive count

3. **Storage Health**
   - Blob storage replication status
   - Available storage space
   - Soft-deleted items count

4. **Recovery Metrics**
   - Last recovery test date
   - Average recovery time
   - Recovery success rate

---

## Appendix

### Backup Contacts

| Role | Name | Phone | Email | Escalation |
|------|------|-------|-------|------------|
| **DR Coordinator** | [Name] | [Phone] | [Email] | Primary |
| **Database Admin** | [Name] | [Phone] | [Email] | Technical |
| **Security Officer** | [Name] | [Phone] | [Email] | Security |
| **Azure Support** | Microsoft | 1800 XXX XXX | - | Vendor |
| **Executive Sponsor** | [Name] | [Phone] | [Email] | Business |

### Backup Storage Accounts

| Account Name | Purpose | Region | Redundancy |
|--------------|---------|--------|------------|
| `admcomplianceprodbackup` | Primary backups | Australia East | GRS |
| `admcompliancetfstate` | Terraform state | Australia East | GRS |
| `admcomplianceprod` | Application files | Australia East | GRS |

### Compliance Requirements

**Australian Privacy Act APP 11:**
- Implement reasonable security measures
- Protect against unauthorized access, modification, disclosure
- Destroy or de-identify information no longer needed

**Data Retention:**
- Audit logs: 7 years minimum
- Personal information: As per Privacy Policy
- Financial records: 7 years
- Compliance reports: 7 years

**Data Sovereignty:**
- All backups must remain in Australian regions
- No data transfer outside Australia
- Geo-replication only to Australian regions

---

**Document Version**: 1.0.0
**Last Reviewed**: 2024-01-XX
**Next Review**: Quarterly
**Owner**: Infrastructure & Security Team
**Approval**: CTO, CISO, Privacy Officer
