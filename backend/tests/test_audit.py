import pytest
from fastapi import status
import uuid
from datetime import datetime, timedelta

from app.models.audit_log import AuditLog
from app.models.document import Document
from app.services.audit_service import audit_service
from app.tasks.audit_tasks import archive_old_audit_logs


class TestAuditService:
    """Tests for audit service"""

    def test_log_action_success(self, created_user):
        """Test successful audit log creation"""
        log = audit_service.log_action(
            user_id=str(created_user.id),
            action="test_action",
            details={"key": "value"},
            ip_address="192.168.1.1",
            user_agent="Test Agent",
        )
        
        assert log.user_id == created_user.id
        assert log.action == "test_action"
        assert log.details == {"key": "value"}
        assert log.ip_address == "192.168.1.1"
        assert log.user_agent == "Test Agent"
        assert log.archived == False

    def test_log_action_sanitizes_passwords(self, created_user):
        """Test that passwords are sanitized in details"""
        log = audit_service.log_action(
            user_id=str(created_user.id),
            action="test_action",
            details={"password": "secret123", "other": "value"},
            ip_address="192.168.1.1",
        )
        
        assert log.details["password"] == "[REDACTED]"
        assert log.details["other"] == "value"

    def test_log_action_sanitizes_tokens(self, created_user):
        """Test that tokens are sanitized in details"""
        log = audit_service.log_action(
            user_id=str(created_user.id),
            action="test_action",
            details={"access_token": "token123", "refresh_token": "refresh123"},
        )
        
        assert log.details["access_token"] == "[REDACTED]"
        assert log.details["refresh_token"] == "[REDACTED]"

    def test_log_action_anonymous(self):
        """Test logging action without user"""
        log = audit_service.log_action(
            user_id=None,
            action="anonymous_action",
            details={"key": "value"},
        )
        
        assert log.user_id is None
        assert log.action == "anonymous_action"

    def test_sanitize_nested_dict(self):
        """Test sanitization of nested dictionaries"""
        details = {
            "user": {
                "email": "test@example.com",
                "password": "secret",
            },
            "token": "abc123",
        }
        
        sanitized = audit_service._sanitize_details(details)
        
        assert sanitized["user"]["password"] == "[REDACTED]"
        assert sanitized["token"] == "[REDACTED]"
        assert sanitized["user"]["email"] == "test@example.com"


class TestAuditEndpoints:
    """Tests for audit log endpoints"""

    def test_get_audit_logs_admin(self, client, admin_auth_headers, created_user, db_session):
        """Test getting audit logs as admin"""
        # Create some audit logs
        for i in range(5):
            log = AuditLog(
                user_id=created_user.id,
                action=f"test_action_{i}",
                details={"test": "data"},
            )
            db_session.add(log)
        db_session.commit()
        
        response = client.get(
            "/api/v1/admin/audit_logs",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 5

    def test_get_audit_logs_pagination(self, client, admin_auth_headers, created_user, db_session):
        """Test audit logs pagination"""
        # Create multiple logs
        for i in range(15):
            log = AuditLog(
                user_id=created_user.id,
                action=f"action_{i}",
            )
            db_session.add(log)
        db_session.commit()
        
        response = client.get(
            "/api/v1/admin/audit_logs?page=1&per_page=10",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 10
        assert data["total"] >= 15
        assert data["page"] == 1

    def test_get_audit_logs_filter_by_user(self, client, admin_auth_headers, created_user, created_admin, db_session):
        """Test filtering audit logs by user"""
        # Create logs for different users
        log1 = AuditLog(
            user_id=created_user.id,
            action="action1",
        )
        log2 = AuditLog(
            user_id=created_admin.id,
            action="action2",
        )
        db_session.add_all([log1, log2])
        db_session.commit()
        
        response = client.get(
            f"/api/v1/admin/audit_logs?filter_user={created_user.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert all(item["user_id"] == str(created_user.id) for item in data["items"])

    def test_get_audit_logs_filter_by_action(self, client, admin_auth_headers, created_user, db_session):
        """Test filtering audit logs by action"""
        # Create logs with different actions
        log1 = AuditLog(
            user_id=created_user.id,
            action="login",
        )
        log2 = AuditLog(
            user_id=created_user.id,
            action="create_document",
        )
        db_session.add_all([log1, log2])
        db_session.commit()
        
        response = client.get(
            "/api/v1/admin/audit_logs?action=login",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert all(item["action"] == "login" for item in data["items"])

    def test_get_audit_logs_student_denied(self, client, auth_headers):
        """Test that students cannot view audit logs"""
        response = client.get(
            "/api/v1/admin/audit_logs",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_audit_logs_unauthorized(self, client):
        """Test getting audit logs without authentication"""
        response = client.get("/api/v1/admin/audit_logs")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_audit_logs_excludes_archived(self, client, admin_auth_headers, created_user, db_session):
        """Test that archived logs are excluded by default"""
        # Create archived and non-archived logs
        log1 = AuditLog(
            user_id=created_user.id,
            action="action1",
            archived=False,
        )
        log2 = AuditLog(
            user_id=created_user.id,
            action="action2",
            archived=True,
        )
        db_session.add_all([log1, log2])
        db_session.commit()
        
        response = client.get(
            "/api/v1/admin/audit_logs",
            headers=admin_auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only return non-archived logs
        assert all(not item["archived"] for item in data["items"])


class TestAuditTask:
    """Tests for audit archive task"""

    @pytest.mark.skipif(True, reason="Requires Celery worker running")
    def test_archive_old_logs(self, created_user, db_session):
        """Test archiving old audit logs"""
        # Create old log (more than 365 days ago)
        old_date = datetime.utcnow() - timedelta(days=400)
        old_log = AuditLog(
            user_id=created_user.id,
            action="old_action",
            archived=False,
            timestamp=old_date,
        )
        
        # Create recent log
        recent_log = AuditLog(
            user_id=created_user.id,
            action="recent_action",
            archived=False,
        )
        
        db_session.add_all([old_log, recent_log])
        db_session.commit()
        
        # Run archive task
        result = archive_old_audit_logs(days=365)
        
        assert result["status"] == "completed"
        assert result["archived_count"] >= 1
        
        # Check that old log is archived
        db_session.refresh(old_log)
        assert old_log.archived == True
        
        # Check that recent log is not archived
        db_session.refresh(recent_log)
        assert recent_log.archived == False

