"""Add analysis algorithm factor fields: hook_strength_score, engagement_velocity_score, etc.

Revision ID: 004_analysis_factors
Revises: a3f9c1d7e2b8
Create Date: 2026-02-21

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_analysis_factors'
down_revision: Union[str, Sequence[str], None] = 'a3f9c1d7e2b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade analyses table schema."""
    # Rename hook_strength to hook_strength_score and change type from String to Float
    op.alter_column('analyses', 'hook_strength',
                    new_column_name='hook_strength_score',
                    type_=sa.Float(),
                    postgresql_using='COALESCE(hook_strength::float, NULL)',
                    existing_type=sa.String(),
                    existing_nullable=True)

    # Rename engagement_velocity to engagement_velocity_score
    op.alter_column('analyses', 'engagement_velocity',
                    new_column_name='engagement_velocity_score',
                    existing_type=sa.Float(),
                    existing_nullable=True)

    # Rename save_share_ratio to save_share_ratio_score
    op.alter_column('analyses', 'save_share_ratio',
                    new_column_name='save_share_ratio_score',
                    existing_type=sa.Float(),
                    existing_nullable=True)

    # Rename hashtag_performance to hashtag_performance_score (keep as JSON for detailed data)
    op.alter_column('analyses', 'hashtag_performance',
                    new_column_name='hashtag_performance_score',
                    existing_type=sa.JSON(),
                    existing_nullable=True)

    # Add new factor columns
    op.add_column('analyses', sa.Column('audience_retention_score', sa.Float(), nullable=True))
    op.add_column('analyses', sa.Column('confidence_score', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade analyses table schema."""
    # Drop new columns
    op.drop_column('analyses', 'confidence_score')
    op.drop_column('analyses', 'audience_retention_score')

    # Revert column renames
    op.alter_column('analyses', 'hashtag_performance_score',
                    new_column_name='hashtag_performance',
                    existing_type=sa.JSON(),
                    existing_nullable=True)

    op.alter_column('analyses', 'save_share_ratio_score',
                    new_column_name='save_share_ratio',
                    existing_type=sa.Float(),
                    existing_nullable=True)

    op.alter_column('analyses', 'engagement_velocity_score',
                    new_column_name='engagement_velocity',
                    existing_type=sa.Float(),
                    existing_nullable=True)

    op.alter_column('analyses', 'hook_strength_score',
                    new_column_name='hook_strength',
                    type_=sa.String(),
                    existing_type=sa.Float(),
                    existing_nullable=True)
