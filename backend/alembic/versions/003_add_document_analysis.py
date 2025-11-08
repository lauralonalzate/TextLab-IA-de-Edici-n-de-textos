"""Add document analysis table

Revision ID: 003_add_document_analysis
Revises: 002_add_document_versions
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_document_analysis'
down_revision = '002_add_document_versions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create document_analysis table
    op.create_table(
        'document_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text_hash', sa.String(64), nullable=False),
        sa.Column('analysis', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_document_analysis_id', 'document_analysis', ['id'])
    op.create_index('idx_document_analysis_document_id', 'document_analysis', ['document_id'])
    op.create_index('idx_document_analysis_text_hash', 'document_analysis', ['text_hash'])
    op.create_index('idx_document_analysis_created_at', 'document_analysis', ['created_at'])
    op.create_index('idx_document_analysis_document_hash', 'document_analysis', ['document_id', 'text_hash'])


def downgrade() -> None:
    op.drop_table('document_analysis')

