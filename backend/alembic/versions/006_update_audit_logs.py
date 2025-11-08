"""Update audit logs table with additional fields

Revision ID: 006_update_audit_logs
Revises: 005_add_document_stats
Create Date: 2024-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_update_audit_logs'
down_revision = '005_add_document_stats'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to audit_logs table
    op.add_column('audit_logs', sa.Column('ip_address', sa.String(45), nullable=True))
    op.add_column('audit_logs', sa.Column('user_agent', sa.String(500), nullable=True))
    op.add_column('audit_logs', sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add indexes
    op.create_index('idx_audit_logs_archived', 'audit_logs', ['archived'])
    op.create_index('idx_audit_logs_user_action', 'audit_logs', ['user_id', 'action'])


def downgrade() -> None:
    op.drop_index('idx_audit_logs_user_action', 'audit_logs')
    op.drop_index('idx_audit_logs_archived', 'audit_logs')
    op.drop_column('audit_logs', 'archived')
    op.drop_column('audit_logs', 'user_agent')
    op.drop_column('audit_logs', 'ip_address')

