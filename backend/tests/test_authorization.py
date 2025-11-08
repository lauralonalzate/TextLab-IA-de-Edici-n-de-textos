import pytest
from fastapi import status


class TestRoleBasedAuthorization:
    """Tests for role-based authorization"""

    def test_admin_stats_with_admin_role(self, client, admin_auth_headers):
        """Test admin stats endpoint with admin role"""
        response = client.get(
            "/api/v1/admin/stats",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "total_documents" in data
        assert "total_users" in data
        assert "total_export_jobs" in data
        assert data["requested_by"]["role"] == "admin"

    def test_admin_stats_with_teacher_role(self, client, teacher_auth_headers):
        """Test admin stats endpoint with teacher role"""
        response = client.get(
            "/api/v1/admin/stats",
            headers=teacher_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "total_documents" in data
        assert "total_users" in data
        assert data["requested_by"]["role"] == "teacher"

    def test_admin_stats_with_student_role(self, client, auth_headers):
        """Test admin stats endpoint with student role (should fail)"""
        response = client.get(
            "/api/v1/admin/stats",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "access denied" in response.json()["detail"].lower()
        assert "required roles" in response.json()["detail"].lower()

    def test_admin_stats_without_authentication(self, client):
        """Test admin stats endpoint without authentication"""
        response = client.get("/api/v1/admin/stats")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_stats_with_invalid_token(self, client):
        """Test admin stats endpoint with invalid token"""
        response = client.get(
            "/api/v1/admin/stats",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_users_me_with_any_role(self, client, auth_headers):
        """Test users/me endpoint works with any authenticated role"""
        response = client.get(
            "/api/v1/users/me",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_users_me_with_admin_role(self, client, admin_auth_headers):
        """Test users/me endpoint works with admin role"""
        response = client.get(
            "/api/v1/users/me",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_users_me_with_teacher_role(self, client, teacher_auth_headers):
        """Test users/me endpoint works with teacher role"""
        response = client.get(
            "/api/v1/users/me",
            headers=teacher_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK


class TestTokenValidation:
    """Tests for token validation and security"""

    def test_token_contains_correct_claims(self, client, created_user, test_user_data):
        """Test that JWT token contains correct claims"""
        import jwt
        from app.core.config import settings
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]
        
        # Decode token (without verification for testing)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert payload["sub"] == str(created_user.id)
        assert payload["email"] == created_user.email
        assert payload["role"] == created_user.role.value
        assert "exp" in payload
        assert "iat" in payload
        assert payload["type"] == "access"

    def test_refresh_token_has_different_type(self, client, created_user, test_user_data):
        """Test that refresh token has type 'refresh'"""
        import jwt
        from app.core.config import settings
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        refresh_token = response.json()["refresh_token"]
        
        # Decode token (without verification for testing)
        payload = jwt.decode(refresh_token, options={"verify_signature": False})
        
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

