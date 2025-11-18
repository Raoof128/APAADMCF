"""
Tests for ADM System Registry endpoints
"""

import pytest
from fastapi import status


class TestADMRegistry:
    """Test ADM System Registry functionality"""

    @pytest.fixture
    def sample_adm_system_data(self):
        """Sample ADM system data for testing"""
        return {
            "name": "Credit Risk Assessment System",
            "description": "Automated credit risk scoring for loan applications",
            "purpose": "Assess creditworthiness of loan applicants",
            "adm_category": "partially_automated",
            "decision_impact": "high",
            "system_status": "production",
            "model_type": "classification",
            "data_retention_period": 2555  # 7 years
        }

    def test_create_adm_system(self, client, auth_headers, sample_adm_system_data):
        """Test creating ADM system"""
        response = client.post(
            "/api/v1/adm/registry",
            json=sample_adm_system_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_adm_system_data["name"]
        assert data["decision_impact"] == "high"
        assert "id" in data

    def test_create_adm_system_unauthorized(self, client, sample_adm_system_data):
        """Test creating ADM system without authentication"""
        response = client.post(
            "/api/v1/adm/registry",
            json=sample_adm_system_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_adm_systems(self, client, auth_headers, sample_adm_system_data):
        """Test listing ADM systems"""
        # Create a system first
        client.post(
            "/api/v1/adm/registry",
            json=sample_adm_system_data,
            headers=auth_headers
        )

        # List systems
        response = client.get(
            "/api/v1/adm/registry",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_adm_system_detail(self, client, auth_headers, sample_adm_system_data):
        """Test getting ADM system details"""
        # Create a system
        create_response = client.post(
            "/api/v1/adm/registry",
            json=sample_adm_system_data,
            headers=auth_headers
        )
        system_id = create_response.json()["id"]

        # Get details
        response = client.get(
            f"/api/v1/adm/registry/{system_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == sample_adm_system_data["name"]
        assert "pia_count" in data
        assert "risk_count" in data

    def test_update_adm_system(self, client, auth_headers, sample_adm_system_data):
        """Test updating ADM system"""
        # Create a system
        create_response = client.post(
            "/api/v1/adm/registry",
            json=sample_adm_system_data,
            headers=auth_headers
        )
        system_id = create_response.json()["id"]

        # Update it
        update_data = {"description": "Updated description"}
        response = client.put(
            f"/api/v1/adm/registry/{system_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_adm_system(self, client, auth_headers, sample_adm_system_data):
        """Test soft-deleting ADM system"""
        # Create a system
        create_response = client.post(
            "/api/v1/adm/registry",
            json=sample_adm_system_data,
            headers=auth_headers
        )
        system_id = create_response.json()["id"]

        # Delete it
        response = client.delete(
            f"/api/v1/adm/registry/{system_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_filter_by_impact(self, client, auth_headers, sample_adm_system_data):
        """Test filtering ADM systems by impact level"""
        # Create systems with different impact levels
        for impact in ["low", "medium", "high"]:
            data = sample_adm_system_data.copy()
            data["name"] = f"System {impact}"
            data["decision_impact"] = impact
            client.post(
                "/api/v1/adm/registry",
                json=data,
                headers=auth_headers
            )

        # Filter for high impact only
        response = client.get(
            "/api/v1/adm/registry?decision_impact=high",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(system["decision_impact"] == "high" for system in data)
