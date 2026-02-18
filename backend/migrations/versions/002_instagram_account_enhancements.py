"""Instagram account enhancements: status, profile data, binary token

Revision ID: 002_instagram_enhancements
Revises: df1349f0b6a4
Create Date: 2026-02-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_instagram_enhancements'
down_revision = 'df1349f0b6a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to instagram_accounts
    op.add_column(
        'instagram_accounts',
        sa.Column('profile_picture', sa.String(), nullable=True)
    )
    op.add_column(
        'instagram_accounts',
        sa.Column('account_type', sa.String(), nullable=True)
    )
    op.add_column(
        'instagram_accounts',
        sa.Column('follower_count', sa.Integer(), nullable=True)
    )
    op.add_column(
        'instagram_accounts',
        sa.Column('status', sa.String(), nullable=False, server_default='active')
    )

    # Rename instagram_username -> username
    op.alter_column(
        'instagram_accounts',
        'instagram_username',
        new_column_name='username',
        existing_type=sa.String()
    )

    # Change access_token from VARCHAR to BYTEA (LargeBinary)
    op.alter_column(
        'instagram_accounts',
        'access_token',
        type_=sa.LargeBinary(),
        postgresql_using='access_token::bytea',
        existing_type=sa.String(),
        existing_nullable=True
    )


def downgrade() -> None:
    # Revert access_token from BYTEA back to VARCHAR
    op.alter_column(
        'instagram_accounts',
        'access_token',
        type_=sa.String(),
        postgresql_using='encode(access_token, \'escape\')',
        existing_type=sa.LargeBinary(),
        existing_nullable=True
    )

    # Rename username back to instagram_username
    op.alter_column(
        'instagram_accounts',
        'username',
        new_column_name='instagram_username',
        existing_type=sa.String()
    )

    # Drop added columns in reverse order
    op.drop_column('instagram_accounts', 'status')
    op.drop_column('instagram_accounts', 'follower_count')
    op.drop_column('instagram_accounts', 'account_type')
    op.drop_column('instagram_accounts', 'profile_picture')
