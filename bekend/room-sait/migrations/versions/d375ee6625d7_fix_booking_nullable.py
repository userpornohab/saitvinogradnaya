"""Fix booking nullable

Revision ID: d375ee6625d7
Revises: e08e886aa0e4
Create Date: 2025-06-24 01:45:44.475469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd375ee6625d7'
down_revision = 'e08e886aa0e4'
branch_labels = None
depends_on = None


def upgrade():
    # Для SQLite ничего не делаем - изменения уже применены
    if op.get_context().dialect.name != 'sqlite':
        op.alter_column('bookings', 'check_in_date', nullable=True)
        op.alter_column('bookings', 'check_out_date', nullable=True)

def downgrade():
    if op.get_context().dialect.name != 'sqlite':
        op.alter_column('bookings', 'check_in_date', nullable=False)
        op.alter_column('bookings', 'check_out_date', nullable=False)