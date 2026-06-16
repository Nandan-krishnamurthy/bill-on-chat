"""add_message_archive_table

Revision ID: 01d90361f059
Revises: 8d1d60b9710b
Create Date: 2026-06-16 17:56:51.516265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '01d90361f059'
down_revision: Union[str, Sequence[str], None] = '8d1d60b9710b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add message_archives table."""
    op.create_table(
        'message_archives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(128), nullable=False),
        sa.Column('thread_id', sa.String(256), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('archived_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('message_archives_pkey')),
    )
    op.create_index(op.f('ix_message_archives_business_id'), 'message_archives', ['business_id'], unique=False)
    op.create_index(op.f('ix_message_archives_session_id'), 'message_archives', ['session_id'], unique=False)
    op.create_index(op.f('ix_message_archives_created_at'), 'message_archives', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop message_archives table."""
    op.drop_index(op.f('ix_message_archives_created_at'), table_name='message_archives')
    op.drop_index(op.f('ix_message_archives_session_id'), table_name='message_archives')
    op.drop_index(op.f('ix_message_archives_business_id'), table_name='message_archives')
    op.drop_table('message_archives')

