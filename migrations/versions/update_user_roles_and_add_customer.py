"""Update User roles and add Customer model

Revision ID: 1a2b3c4d5e6f
Revises: bd5c5a96e218
Create Date: 2025-10-19 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = 'bd5c5a96e218'
branch_labels = None
depends_on = None

def upgrade():
    # Create customers table first
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False, index=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_ride_at', sa.DateTime(), nullable=True),
        sa.Column('total_rides', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_phone'), 'customers', ['phone'], unique=True)
    
    # Add customer_id to rides as nullable first
    op.add_column('rides', sa.Column('customer_id', sa.Integer(), nullable=True))
    
    # Add is_dispatcher column to users
    op.add_column('users', sa.Column('is_dispatcher', sa.Boolean(), nullable=True, server_default='0'))
    
    # Update existing users to have is_dispatcher=False if not set
    op.execute("UPDATE users SET is_dispatcher = 0 WHERE is_dispatcher IS NULL")
    
    # Make phone, password, and full_name required
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('phone', existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('password', existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('full_name', existing_type=sa.VARCHAR(), nullable=False)
    
    # Add foreign key constraint for customer_id in rides
    op.create_foreign_key('fk_rides_customer_id', 'rides', 'customers', ['customer_id'], ['id'])
    
    # For existing rides, you'll need to create customer records and update the customer_id
    # This is a simplified example - you may need to adjust based on your data
    op.execute("""
        INSERT INTO customers (phone, first_name, last_name, created_at, last_ride_at, total_rides)
        SELECT DISTINCT u.phone, u.full_name, '', u.created_at, MAX(r.created_at), COUNT(r.id)
        FROM users u
        JOIN rides r ON u.id = r.rider_id
        GROUP BY u.id, u.phone, u.full_name, u.created_at
    """)
    
    # Update rides with customer_id
    op.execute("""
        UPDATE rides
        SET customer_id = (SELECT id FROM customers WHERE phone = (SELECT phone FROM users WHERE id = rides.rider_id))
        WHERE customer_id IS NULL
    """)
    
    # Now make customer_id required
    with op.batch_alter_table('rides') as batch_op:
        batch_op.alter_column('customer_id', nullable=False)

def downgrade():
    # Drop the foreign key first
    with op.batch_alter_table('rides') as batch_op:
        batch_op.drop_constraint('fk_rides_customer_id', type_='foreignkey')
    
    # Make customer_id nullable before dropping
    with op.batch_alter_table('rides') as batch_op:
        batch_op.alter_column('customer_id', nullable=True)
    
    # Drop the customers table
    op.drop_table('customers')
    
    # Remove is_dispatcher column
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('is_dispatcher')
    
    # Make columns nullable again (if needed)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('phone', existing_type=sa.VARCHAR(), nullable=True)
        batch_op.alter_column('password', existing_type=sa.VARCHAR(), nullable=True)
        batch_op.alter_column('full_name', existing_type=sa.VARCHAR(), nullable=True)
