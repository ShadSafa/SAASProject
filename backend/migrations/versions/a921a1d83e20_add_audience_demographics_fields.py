"""add_audience_demographics_fields

Revision ID: a921a1d83e20
Revises: 004_analysis_factors
Create Date: 2026-02-21 15:51:31.946920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a921a1d83e20'
down_revision: Union[str, Sequence[str], None] = '004_analysis_factors'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add audience demographics fields to analyses table
    op.add_column('analyses', sa.Column('engagement_rate', sa.Float(), nullable=True))
    op.add_column('analyses', sa.Column('audience_interests', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove audience demographics fields from analyses table
    op.drop_column('analyses', 'audience_interests')
    op.drop_column('analyses', 'engagement_rate')
