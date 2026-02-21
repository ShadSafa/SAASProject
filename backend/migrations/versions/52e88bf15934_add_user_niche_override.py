"""add_user_niche_override

Revision ID: 52e88bf15934
Revises: a921a1d83e20
Create Date: 2026-02-21 16:43:22.722175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52e88bf15934'
down_revision: Union[str, Sequence[str], None] = 'a921a1d83e20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('analyses', sa.Column('user_niche_override', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analyses', 'user_niche_override')
