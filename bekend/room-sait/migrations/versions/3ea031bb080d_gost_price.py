"""gost_price

Revision ID: 3ea031bb080d
Revises: 23f3dcaa934d
Create Date: 2025-06-23 00:02:30.495944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ea031bb080d'
down_revision: Union[str, None] = '23f3dcaa934d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Удаление user_id
    op.drop_constraint('fk_bookings_user_id', 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'user_id')
    
    # Добавление новых колонок с nullable=True
    op.add_column('bookings', sa.Column('guest_name', sa.String(length=100), nullable=True))
    op.add_column('bookings', sa.Column('guest_phone', sa.String(length=20), nullable=True))
    op.add_column('bookings', sa.Column('guest_comment', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('bookings') as batch_op:
        batch_op.drop_column('guest_comment')
        batch_op.drop_column('guest_phone')
        batch_op.drop_column('guest_name')
    
    op.add_column('bookings', sa.Column('user_id', sa.INTEGER(), nullable=True))
    op.create_foreign_key('fk_bookings_user_id', 'bookings', 'users', ['user_id'], ['id'])