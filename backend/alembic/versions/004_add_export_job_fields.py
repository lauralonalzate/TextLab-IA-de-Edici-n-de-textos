"""Add export job fields

Revision ID: 004_add_export_job_fields
Revises: 003_add_document_analysis
Create Date: 2024-01-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_export_job_fields'
down_revision = '003_add_document_analysis'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to export_jobs table
    op.add_column('export_jobs', sa.Column('export_format', sa.String(10), nullable=True, server_default='pdf'))
    op.add_column('export_jobs', sa.Column('include_stats', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('export_jobs', sa.Column('template_id', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('export_jobs', 'template_id')
    op.drop_column('export_jobs', 'include_stats')
    op.drop_column('export_jobs', 'export_format')

