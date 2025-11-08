"""Add document stats table

Revision ID: 005_add_document_stats
Revises: 004_add_export_job_fields
Create Date: 2024-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_document_stats'
down_revision = '004_add_export_job_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create document_stats table
    op.create_table(
        'document_stats',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stats', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_document_stats_id', 'document_stats', ['id'])
    op.create_index('idx_document_stats_document_id', 'document_stats', ['document_id'])
    op.create_index('idx_document_stats_created_at', 'document_stats', ['created_at'])


def downgrade() -> None:
    op.drop_table('document_stats')

