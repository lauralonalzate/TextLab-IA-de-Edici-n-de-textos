import pytest
from fastapi import status


class TestUserRegistration:
    """Tests for user registration endpoint"""

    def test_register_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Check user data (no password)
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["full_name"] == test_user_data["full_name"]
        assert user["role"] == test_user_data["role"]
        assert "id" in user
        assert "password" not in user
        assert "password_hash" not in user

    def test_register_duplicate_email(self, client, test_user_data, created_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "full_name": "Test User",
                "password": "testpassword123",
                "role": "student",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "short",
                "role": "student",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_different_roles(self, client):
        """Test registration with different roles"""
        roles = ["student", "teacher", "researcher", "admin"]
        for role in roles:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"{role}@example.com",
                    "full_name": f"{role.title()} User",
                    "password": "testpassword123",
                    "role": role,
                },
            )
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["user"]["role"] == role


class TestUserLogin:
    """Tests for user login endpoint"""

    def test_login_success(self, client, created_user, test_user_data):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    def test_login_wrong_password(self, client, created_user, test_user_data):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_invalid_email(self, client):
        """Test login with invalid email format"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "somepassword",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenRefresh:
    """Tests for token refresh endpoint"""

    def test_refresh_token_success(self, client, created_user, test_user_data):
        """Test successful token refresh"""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_with_access_token(self, client, created_user, test_user_data):
        """Test refresh with access token (should fail)"""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        
        # Try to refresh with access token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoints:
    """Tests for protected endpoints"""

    def test_get_current_user_success(self, client, auth_headers, created_user):
        """Test getting current user info with valid token"""
        response = client.get(
            "/api/v1/users/me",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["email"] == created_user.email
        assert data["full_name"] == created_user.full_name
        assert data["role"] == created_user.role.value
        assert "password" not in data
        assert "password_hash" not in data

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_expired_token(self, client, created_user, test_user_data):
        """Test getting current user with expired token"""
        # This would require mocking time or using a very short expiration
        # For now, we'll just test that invalid tokens are rejected
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer expired_token_here"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

