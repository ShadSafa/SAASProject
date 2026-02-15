"""Initial schema with all tables

Revision ID: df1349f0b6a4
Revises: 
Create Date: 2026-02-15 21:42:04.869684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df1349f0b6a4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create instagram_accounts table
    op.create_table(
        'instagram_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('instagram_user_id', sa.String(), nullable=False),
        sa.Column('instagram_username', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'instagram_user_id', name='uix_user_instagram')
    )
    op.create_index('ix_instagram_accounts_user_id', 'instagram_accounts', ['user_id'], unique=False)

    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('time_range', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_usage table
    op.create_table(
        'user_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('scans_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_reset_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_usage_user_id_month', 'user_usage', ['user_id', 'month'], unique=False)

    # Create viral_posts table
    op.create_table(
        'viral_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('instagram_post_id', sa.String(), nullable=False),
        sa.Column('instagram_url', sa.String(), nullable=True),
        sa.Column('post_type', sa.String(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('creator_username', sa.String(), nullable=True),
        sa.Column('creator_follower_count', sa.Integer(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=True),
        sa.Column('saves_count', sa.Integer(), nullable=True),
        sa.Column('shares_count', sa.Integer(), nullable=True),
        sa.Column('viral_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('instagram_post_id')
    )

    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('viral_post_id', sa.Integer(), nullable=False),
        sa.Column('why_viral_summary', sa.Text(), nullable=True),
        sa.Column('hook_strength', sa.String(), nullable=True),
        sa.Column('emotional_trigger', sa.String(), nullable=True),
        sa.Column('posting_time_score', sa.Float(), nullable=True),
        sa.Column('engagement_velocity', sa.Float(), nullable=True),
        sa.Column('save_share_ratio', sa.Float(), nullable=True),
        sa.Column('hashtag_performance', sa.JSON(), nullable=True),
        sa.Column('audience_demographics', sa.JSON(), nullable=True),
        sa.Column('content_category', sa.String(), nullable=True),
        sa.Column('niche', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['viral_post_id'], ['viral_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('viral_post_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('analyses')
    op.drop_table('viral_posts')
    op.drop_table('user_usage')
    op.drop_index('ix_user_usage_user_id_month', table_name='user_usage')
    op.drop_table('scans')
    op.drop_index('ix_instagram_accounts_user_id', table_name='instagram_accounts')
    op.drop_table('instagram_accounts')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
