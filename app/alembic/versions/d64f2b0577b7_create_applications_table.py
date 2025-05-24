"""create applications table

Revision ID: d64f2b0577b7
Revises: 
Create Date: 2025-05-23 14:39:00.308405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd64f2b0577b7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirement', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
