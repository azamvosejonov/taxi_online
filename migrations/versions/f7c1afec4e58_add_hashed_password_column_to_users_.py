"""Add hashed_password column to users table

Revision ID: f7c1afec4e58
Revises: 
Create Date: 2025-11-02 14:59:33.726391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7c1afec4e58'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False, server_default=''))
    # Make the column non-nullable after adding it with a default value to avoid errors
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hashed_password')



#source .venv/bin/activate &&