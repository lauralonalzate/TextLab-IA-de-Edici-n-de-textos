import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models.user import User, UserRole
from app.utils.auth import hash_password

# Use test database URL from env or default to PostgreSQL test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://testuser:testpass@localhost:5432/testdb"
)

# For PostgreSQL tests (recommended), use: postgresql://user:pass@localhost/test_db
# For SQLite (simpler but limited), use: sqlite:///./test.db

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    # Drop all tables and recreate for clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
        db.rollback()  # Rollback any uncommitted changes
    finally:
        db.close()
        # Clean up: drop all tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close here, let fixture handle it
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "role": "student",
    }


@pytest.fixture
def test_admin_data():
    """Sample admin user data for testing"""
    return {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password": "adminpassword123",
        "role": "admin",
    }


@pytest.fixture
def test_teacher_data():
    """Sample teacher user data for testing"""
    return {
        "email": "teacher@example.com",
        "full_name": "Teacher User",
        "password": "teacherpassword123",
        "role": "teacher",
    }


@pytest.fixture
def created_user(db_session, test_user_data):
    """Create a user in the database for testing"""
    user = User(
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        password_hash=hash_password(test_user_data["password"]),
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def created_admin(db_session, test_admin_data):
    """Create an admin user in the database for testing"""
    user = User(
        email=test_admin_data["email"],
        full_name=test_admin_data["full_name"],
        password_hash=hash_password(test_admin_data["password"]),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def created_teacher(db_session, test_teacher_data):
    """Create a teacher user in the database for testing"""
    user = User(
        email=test_teacher_data["email"],
        full_name=test_teacher_data["full_name"],
        password_hash=hash_password(test_teacher_data["password"]),
        role=UserRole.TEACHER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, created_user, test_user_data):
    """Get authentication headers for a test user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, created_admin, test_admin_data):
    """Get authentication headers for an admin user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_admin_data["email"],
            "password": test_admin_data["password"],
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def teacher_auth_headers(client, created_teacher, test_teacher_data):
    """Get authentication headers for a teacher user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_teacher_data["email"],
            "password": test_teacher_data["password"],
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

