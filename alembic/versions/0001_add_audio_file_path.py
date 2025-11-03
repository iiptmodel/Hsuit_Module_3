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
    # Add a nullable string column for audio file path
    op.add_column('chat_messages', sa.Column('audio_file_path', sa.String(), nullable=True))


def downgrade():
    # Remove the audio_file_path column
    op.drop_column('chat_messages', 'audio_file_path')
