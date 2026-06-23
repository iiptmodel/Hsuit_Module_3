"""add mime_type and thumbnail_path to reports

Revision ID: 9f1b_add_mime_and_thumbnail_to_reports
Revises: 0001_add_audio_file_path
Create Date: 2025-11-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9f1b_add_mime_and_thumbnail_to_reports'
# Chain this after the last original_filename migration to avoid branching
down_revision = '78241e41fccb'
branch_labels = None
depends_on = None


def upgrade():
    # Skip if the table is missing; add each column only if it doesn't exist.
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('reports'):
        return
    columns = [col['name'] for col in inspector.get_columns('reports')]
    if 'mime_type' not in columns:
        op.add_column('reports', sa.Column('mime_type', sa.String(), nullable=True))
    if 'thumbnail_path' not in columns:
        op.add_column('reports', sa.Column('thumbnail_path', sa.String(), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('reports'):
        return
    columns = [col['name'] for col in inspector.get_columns('reports')]
    if 'thumbnail_path' in columns:
        op.drop_column('reports', 'thumbnail_path')
    if 'mime_type' in columns:
        op.drop_column('reports', 'mime_type')
