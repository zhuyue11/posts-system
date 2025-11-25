"""Add subject column to posts table

Revision ID: 20251125112935
Revises: 3691979bb9f2
Create Date: 2025-11-25 11:29:35

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251125112935'
down_revision: Union[str, None] = '3691979bb9f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add subject column to posts table
    op.add_column('posts', sa.Column('subject', sa.String(length=255), nullable=False))


def downgrade() -> None:
    # Remove subject column from posts table
    op.drop_column('posts', 'subject')
