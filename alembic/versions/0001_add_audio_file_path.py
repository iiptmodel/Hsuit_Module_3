"""add audio_file_path to chat_messages

Revision ID: 0001_add_audio_file_path
Revises: 
Create Date: 2025-11-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_audio_file_path'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Skip if the table or column already exists (tables are created by
    # Base.metadata.create_all() at app startup; this keeps the migration
    # idempotent and safe to run on an already-provisioned database).
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('chat_messages'):
        return
    columns = [col['name'] for col in inspector.get_columns('chat_messages')]
    if 'audio_file_path' not in columns:
        # Add a nullable string column for audio file path
        op.add_column('chat_messages', sa.Column('audio_file_path', sa.String(), nullable=True))


def downgrade():
    # Remove the column only if it exists.
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('chat_messages'):
        return
    columns = [col['name'] for col in inspector.get_columns('chat_messages')]
    if 'audio_file_path' in columns:
        op.drop_column('chat_messages', 'audio_file_path')
