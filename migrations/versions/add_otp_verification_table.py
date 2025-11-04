"""Add OTP verification table

Revision ID: otp_verification_001
Revises: f7c1afec4e58
Create Date: 2025-11-04 14:21:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'otp_verification_001'
down_revision: Union[str, Sequence[str], None] = 'f7c1afec4e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'otp_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('otp_code', sa.String(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otp_verifications_phone'), 'otp_verifications', ['phone'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_otp_verifications_phone'), table_name='otp_verifications')
    op.drop_table('otp_verifications')
