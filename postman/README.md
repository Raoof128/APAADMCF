# ADM Compliance Framework - Postman Collection

This directory contains Postman collections and environments for testing the ADM Compliance Framework API.

## Contents

- `ADM_Compliance_API.postman_collection.json` - Complete API collection with all endpoints
- `ADM_Compliance_Local.postman_environment.json` - Environment for local development
- `ADM_Compliance_Production.postman_environment.json` - Environment for production

## Quick Start

### 1. Import Collection and Environment

**Option A: Import via URL (if hosted)**
1. Open Postman
2. Click **Import** button
3. Select **Link** tab
4. Paste the raw GitHub URL to the collection file
5. Click **Continue** → **Import**

**Option B: Import from File**
1. Open Postman
2. Click **Import** button
3. Select **File** tab
4. Choose `ADM_Compliance_API.postman_collection.json`
5. Click **Open**
6. Repeat for environment files

### 2. Select Environment

1. In Postman, click the environment dropdown (top right)
2. Select **ADM Compliance - Local Development** (or Production)
3. Verify the `base_url` is correct

### 3. Start Local Development Environment

Before using the collection, ensure the backend is running:

```bash
# Using Docker Compose (recommended)
cd /path/to/adm-compliance-framework
make quickstart

# Or manually
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

### 4. Run Your First Request

1. In Postman, expand the collection
2. Navigate to **Authentication** → **Login**
3. Click **Send**
4. The response will automatically save the `access_token` to your environment

### 5. Test Other Endpoints

Now you can test other endpoints. They will automatically use the saved token:

1. **Create ADM System** - `POST /adm-systems`
2. **Create PIA** - `POST /pias`
3. **Create Fairness Assessment** - `POST /fairness/assessments`
4. **Submit Individual Request** - `POST /requests`

## Collection Structure

The collection is organized into the following folders:

### 1. Authentication
- Register User
- Login (saves token automatically)
- Get Current User
- Refresh Token

### 2. ADM Systems
- Create ADM System (saves ID automatically)
- List ADM Systems
- Get ADM System
- Update ADM System
- Delete ADM System
- Export ADM Systems (CSV)

### 3. Privacy Impact Assessments
- Create PIA (saves ID automatically)
- List PIAs
- Get PIA
- Complete PIA
- Download PIA Report (PDF)

### 4. Fairness Assessments
- Create Fairness Assessment (saves ID automatically)
- List Fairness Assessments
- Get Fairness Assessment
- Get Fairness Metrics

### 5. Individual Rights Requests
- Submit Access Request (public, no auth)
- Track Request Status (public)
- List Requests (privacy officer)
- Get Request Details
- Respond to Request

### 6. Compliance Monitoring
- Get Compliance Dashboard
- Run Compliance Check
- List Compliance Checks

### 7. Reports
- Generate Compliance Report
- Check Report Status

### 8. Health Check
- Health Check (no auth required)

## Environment Variables

### Local Development Environment

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `base_url` | `http://localhost:8000/api` | API base URL |
| `frontend_url` | `http://localhost:3000` | Frontend URL |
| `access_token` | (auto-set) | JWT access token |
| `refresh_token` | (auto-set) | JWT refresh token |
| `test_user_email` | `privacy.officer@example.gov.au` | Test user email |
| `test_user_password` | `SecurePassword123!` | Test user password |

### Production Environment

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `base_url` | `https://api.adm-compliance.gov.au/api` | API base URL |
| `frontend_url` | `https://adm-compliance.gov.au` | Frontend URL |
| `access_token` | (auto-set) | JWT access token |
| `refresh_token` | (auto-set) | JWT refresh token |
| `test_user_email` | (configure) | Your user email |
| `test_user_password` | (configure) | Your user password |

### Collection Variables (Auto-Set)

These variables are automatically set by test scripts:

- `adm_system_id` - Set after creating an ADM system
- `pia_id` - Set after creating a PIA
- `fairness_assessment_id` - Set after creating a fairness assessment
- `request_id` - Set after submitting an individual request
- `report_task_id` - Set after initiating report generation

## Authentication Flow

The collection uses automated token management:

1. **Login**: Run the **Login** request
   - Test script automatically saves `access_token` and `refresh_token`
   - Token is used for all subsequent requests

2. **Token Expiry**: If you receive a 401 error
   - Run the **Refresh Token** request
   - Or run **Login** again

3. **Collection-Level Auth**:
   - Bearer token is configured at collection level
   - Uses `{{access_token}}` variable
   - Automatically applied to all requests (except public endpoints)

## Test Scripts

Many requests include test scripts that:

- **Validate Response**: Check status codes and response structure
- **Save Variables**: Automatically extract and save IDs from responses
- **Chain Requests**: Enable running requests in sequence

Example workflow:
```
1. Login → saves access_token
2. Create ADM System → saves adm_system_id
3. Create PIA → uses adm_system_id from step 2
4. Complete PIA → uses pia_id from step 3
5. Download PIA Report → uses pia_id
```

## Running Collection with Newman (CLI)

You can run the collection from the command line using Newman:

### Install Newman

```bash
npm install -g newman
```

### Run Collection

```bash
# Run with local environment
newman run ADM_Compliance_API.postman_collection.json \
  -e ADM_Compliance_Local.postman_environment.json

# Run with production environment (requires credentials)
newman run ADM_Compliance_API.postman_collection.json \
  -e ADM_Compliance_Production.postman_environment.json \
  --env-var "test_user_email=your-email@example.gov.au" \
  --env-var "test_user_password=YourPassword"

# Run specific folder
newman run ADM_Compliance_API.postman_collection.json \
  -e ADM_Compliance_Local.postman_environment.json \
  --folder "Authentication"

# Generate HTML report
newman run ADM_Compliance_API.postman_collection.json \
  -e ADM_Compliance_Local.postman_environment.json \
  -r html \
  --reporter-html-export newman-report.html
```

## Example Workflows

### Workflow 1: Complete PIA Process

1. **Login**
2. **Create ADM System**
3. **Create PIA** (uses ADM system ID from step 2)
4. **Complete PIA** (uses PIA ID from step 3)
5. **Download PIA Report**

### Workflow 2: Fairness Assessment

1. **Login**
2. **Create ADM System** (if not exists)
3. **Create Fairness Assessment** with demo data
4. **Get Fairness Assessment** - view results
5. **Get Fairness Metrics** - detailed metrics by protected attribute

### Workflow 3: Individual Request (Public)

1. **Submit Access Request** (no auth required)
   - Note the `tracking_id` from response
2. **Track Request Status** using tracking ID (no auth required)

### Workflow 4: Privacy Officer Request Handling

1. **Login** as privacy officer
2. **List Requests** - filter by status
3. **Get Request Details** - full request information
4. **Respond to Request** - provide response and documents

## Tips and Best Practices

### 1. Use Collection Runner

For testing workflows:
1. Select the collection or folder
2. Click **Run** button
3. Select environment
4. Click **Run ADM Compliance Framework API**

### 2. Save Responses

To save response examples:
1. Send a request
2. Click **Save Response** → **Save as Example**
3. Add description

### 3. Environment Management

- **Never commit production credentials** to version control
- Use separate environments for each deployment
- Use Postman Vault for sensitive data

### 4. Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| **401 Unauthorized** | Token expired | Run **Refresh Token** or **Login** again |
| **403 Forbidden** | Insufficient permissions | Login with appropriate role |
| **404 Not Found** | Resource doesn't exist | Check IDs in environment variables |
| **422 Validation Error** | Invalid request data | Check request body format |
| **Connection Refused** | Backend not running | Start backend: `docker-compose up -d` |

### 5. Testing Fairness Assessments

The demo fairness assessment uses minimal data. For realistic results:

1. Prepare a CSV file with prediction data (see API_EXAMPLES.md)
2. In Postman, use **form-data** body type
3. Add file field: `dataset` → select your CSV
4. Add other fields: `adm_system_id`, `protected_attributes`, `outcome_column`

Format:
```csv
id,gender,age_group,indigenous_status,approved,prediction_score
1,male,25-34,no,1,0.87
2,female,35-44,no,1,0.92
...
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: docker-compose up -d

      - name: Wait for services
        run: sleep 30

      - name: Install Newman
        run: npm install -g newman

      - name: Run API tests
        run: |
          newman run postman/ADM_Compliance_API.postman_collection.json \
            -e postman/ADM_Compliance_Local.postman_environment.json \
            -r cli,json \
            --reporter-json-export results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: newman-results
          path: results.json
```

## Additional Resources

- **API Documentation**: See [API_EXAMPLES.md](../API_EXAMPLES.md) for detailed examples
- **Architecture**: See [ARCHITECTURE.md](../ARCHITECTURE.md) for system design
- **Deployment**: See [DEPLOYMENT.md](../DEPLOYMENT.md) for deployment procedures
- **OpenAPI Spec**: Access live at `http://localhost:8000/api/docs`

## Support

For issues or questions:
- **Bug Reports**: Create an issue in GitHub
- **API Questions**: See API_EXAMPLES.md
- **Deployment Issues**: See DEPLOYMENT.md

---

**Version**: 1.0.0
**Last Updated**: 2024-01-XX
**Maintained by**: API Team
