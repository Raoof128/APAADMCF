# Quick Start Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

## Option 1: Docker Compose (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/yourusername/APAADMCF.git
cd APAADMCF

# Start all services
./scripts/start-dev.sh
```

This will:
- Build Docker images
- Start PostgreSQL, Redis, Backend, and Frontend
- Initialize the database
- Set up the application

**Access the application:**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs
- Backend API: http://localhost:8000

**Default Credentials:**
- Email: `admin@example.gov.au`
- Password: `Admin123!`

⚠️ **IMPORTANT:** Change these credentials immediately!

## Option 2: Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Create database
createdb adm_compliance
psql adm_compliance < database_schema.sql

# Run migrations (optional)
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Access at http://localhost:3000

## Option 3: Production Deployment (Azure)

```bash
# Set up Azure credentials
az login

# Navigate to infrastructure
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Deploy application
kubectl apply -f ../../k8s/
```

See [docs/deployment.md](docs/deployment.md) for detailed deployment instructions.

## Verifying Installation

### 1. Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "Australian Privacy Act ADM Compliance Framework",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Login

Visit http://localhost:3000 and login with the default credentials.

### 3. Explore API

Visit http://localhost:8000/api/docs for interactive API documentation.

## Generate Demo Data

```bash
./scripts/generate-demo-data.sh
```

This creates synthetic datasets for:
- Credit risk assessment
- Fraud detection
- Hiring decisions

## Run Tests

```bash
./scripts/run-tests.sh
```

This runs:
- Unit tests
- Integration tests
- Code linting
- Type checking

## Common Issues

### Port Already in Use

If ports 3000, 5432, or 8000 are already in use:

```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Permission Errors

```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix data directory permissions
chmod -R 755 backend/uploads
```

## Next Steps

1. **Change Default Credentials**
   - Login and go to Settings
   - Update admin password

2. **Register an ADM System**
   - Navigate to ADM Registry
   - Click "Register New System"

3. **Create a PIA**
   - Select an ADM system
   - Start Privacy Impact Assessment

4. **Run Fairness Assessment**
   - Upload demo dataset
   - Run fairness metrics

5. **Explore Compliance Dashboard**
   - View alerts and metrics
   - Monitor drift detection

## Documentation

- [Full Documentation](docs/)
- [Privacy Act Guide](docs/PRIVACY_ACT_ADM_GUIDE.md)
- [API Reference](http://localhost:8000/api/docs)
- [Architecture](docs/architecture.md)

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/APAADMCF/issues
- Documentation: https://docs.example.com
- Email: support@example.com

## Security Note

This framework handles sensitive compliance data. Ensure you:
- Change all default passwords
- Use HTTPS in production
- Enable encryption at rest
- Configure proper RBAC
- Review security settings in production

For production deployment, see [Production Security Checklist](docs/security-checklist.md).
