"""fix notifications schema mismatch

Revision ID: fix_notifications_schema
Revises: 5be11687e9ca
Create Date: 2026-02-06 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'fix_notifications_schema'
down_revision = '5be11687e9ca'
branch_labels = None
depends_on = None


def upgrade():
    # Make this migration idempotent for environments where schema drift already happened
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c['name']: c for c in inspector.get_columns('notifications')}

    needs_is_read_reset = False
    if 'is_read' in cols:
        # If is_read exists but not boolean, rebuild it
        needs_is_read_reset = not isinstance(cols['is_read']['type'], sa.Boolean)

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        if needs_is_read_reset:
            batch_op.drop_column('is_read')
            batch_op.add_column(sa.Column('is_read', sa.Boolean(), nullable=True))
        elif 'is_read' not in cols:
            batch_op.add_column(sa.Column('is_read', sa.Boolean(), nullable=True))

        if 'read_at' not in cols:
            batch_op.add_column(sa.Column('read_at', sa.DateTime(), nullable=True))


def downgrade():
    # Revert the changes
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        # Drop read_at column
        batch_op.drop_column('read_at')
        
        # Drop the Boolean is_read column
        batch_op.drop_column('is_read')
        
        # Recreate the original DateTime is_read column
        batch_op.add_column(sa.Column('is_read', sa.DateTime(), nullable=True))

