"""add language to chat_sessions

Revision ID: 9971bb4842e6
Revises: 9f1b_add_mime_and_thumbnail_to_reports
Create Date: 2026-06-23 23:03:09.249061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9971bb4842e6'
down_revision: Union[str, Sequence[str], None] = '9f1b_add_mime_and_thumbnail_to_reports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('chat_sessions'):
        return
    columns = [col['name'] for col in inspector.get_columns('chat_sessions')]
    if 'language' not in columns:
        op.add_column(
            'chat_sessions',
            sa.Column('language', sa.String(), nullable=False, server_default='English')
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not inspector.has_table('chat_sessions'):
        return
    columns = [col['name'] for col in inspector.get_columns('chat_sessions')]
    if 'language' in columns:
        op.drop_column('chat_sessions', 'language')
