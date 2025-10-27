"""Update User roles and add Customer model (simplified)

Revision ID: 2b3c4d5e6f7a
Revises: bd5c5a96e218
Create Date: 2025-10-19 01:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7a'
down_revision = 'bd5c5a96e218'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Create customers table
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('last_ride_at', sa.DateTime(), nullable=True),
        sa.Column('total_rides', sa.Integer(), server_default='0', nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone', name='uq_customers_phone')
    )
    
    # Create index on phone for faster lookups
    op.create_index(op.f('ix_customers_phone'), 'customers', ['phone'], unique=True)
    
    # Step 2: Add is_dispatcher column to users
    op.add_column('users', sa.Column('is_dispatcher', sa.Boolean(), server_default='0', nullable=True))
    
    # Step 3: Make phone required (in a separate transaction)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('phone', existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('password', existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('full_name', existing_type=sa.VARCHAR(), nullable=False)
    
    # Step 4: Add customer_id to rides (nullable first)
    op.add_column('rides', sa.Column('customer_id', sa.Integer(), nullable=True))
    
    # Note: You'll need to populate customer_id for existing rides in a separate step

def downgrade():
    # Drop the customer_id column
    with op.batch_alter_table('rides') as batch_op:
        batch_op.drop_column('customer_id')
    
    # Make columns nullable again
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('full_name', existing_type=sa.VARCHAR(), nullable=True)
        batch_op.alter_column('password', existing_type=sa.VARCHAR(), nullable=True)
        batch_op.alter_column('phone', existing_type=sa.VARCHAR(), nullable=True)
        batch_op.drop_column('is_dispatcher')
    
    # Drop the customers table
    op.drop_table('customers')
