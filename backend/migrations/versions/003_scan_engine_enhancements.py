"""Scan engine enhancements: scan_type, error_message, BigInteger counts, thumbnail_s3_url

Revision ID: a3f9c1d7e2b8
Revises: 002_instagram_enhancements
Create Date: 2026-02-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a3f9c1d7e2b8'
down_revision: Union[str, Sequence[str], None] = '002_instagram_enhancements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # scans table: add scan_type, target_url, error_message
    op.add_column('scans', sa.Column('scan_type', sa.String(), nullable=False, server_default='hashtag'))
    op.add_column('scans', sa.Column('target_url', sa.String(), nullable=True))
    op.add_column('scans', sa.Column('error_message', sa.Text(), nullable=True))

    # viral_posts table: add new fields, change integer columns to biginteger
    op.add_column('viral_posts', sa.Column('caption', sa.Text(), nullable=True))
    op.add_column('viral_posts', sa.Column('hashtags', sa.Text(), nullable=True))
    op.add_column('viral_posts', sa.Column('thumbnail_s3_url', sa.String(), nullable=True))
    op.add_column('viral_posts', sa.Column('post_age_hours', sa.Float(), nullable=True))

    # Change Integer to BigInteger for engagement counts
    op.alter_column('viral_posts', 'creator_follower_count',
                    existing_type=sa.Integer(), type_=sa.BigInteger(), existing_nullable=True)
    op.alter_column('viral_posts', 'likes_count',
                    existing_type=sa.Integer(), type_=sa.BigInteger(), existing_nullable=True)
    op.alter_column('viral_posts', 'comments_count',
                    existing_type=sa.Integer(), type_=sa.BigInteger(), existing_nullable=True)
    op.alter_column('viral_posts', 'saves_count',
                    existing_type=sa.Integer(), type_=sa.BigInteger(), existing_nullable=True)
    op.alter_column('viral_posts', 'shares_count',
                    existing_type=sa.Integer(), type_=sa.BigInteger(), existing_nullable=True)

    # Drop unique constraint on instagram_post_id (same post can appear in multiple scans)
    op.drop_constraint('viral_posts_instagram_post_id_key', 'viral_posts', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint('viral_posts_instagram_post_id_key', 'viral_posts', ['instagram_post_id'])
    op.alter_column('viral_posts', 'shares_count',
                    existing_type=sa.BigInteger(), type_=sa.Integer(), existing_nullable=True)
    op.alter_column('viral_posts', 'saves_count',
                    existing_type=sa.BigInteger(), type_=sa.Integer(), existing_nullable=True)
    op.alter_column('viral_posts', 'comments_count',
                    existing_type=sa.BigInteger(), type_=sa.Integer(), existing_nullable=True)
    op.alter_column('viral_posts', 'likes_count',
                    existing_type=sa.BigInteger(), type_=sa.Integer(), existing_nullable=True)
    op.alter_column('viral_posts', 'creator_follower_count',
                    existing_type=sa.BigInteger(), type_=sa.Integer(), existing_nullable=True)
    op.drop_column('viral_posts', 'post_age_hours')
    op.drop_column('viral_posts', 'thumbnail_s3_url')
    op.drop_column('viral_posts', 'hashtags')
    op.drop_column('viral_posts', 'caption')
    op.drop_column('scans', 'error_message')
    op.drop_column('scans', 'target_url')
    op.drop_column('scans', 'scan_type')
