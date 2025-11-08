"""Add document versions table

Revision ID: 002_add_document_versions
Revises: 001_initial_schema
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_document_versions'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create documents_versions table
    op.create_table(
        'documents_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_documents_versions_id', 'documents_versions', ['id'])
    op.create_index('idx_document_versions_document_id', 'documents_versions', ['document_id'])
    op.create_index('idx_document_versions_created_at', 'documents_versions', ['created_at'])


def downgrade() -> None:
    op.drop_table('documents_versions')

