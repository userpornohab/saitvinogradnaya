"""Initial

Revision ID: 4b53f1935d90
Revises: 83d0921ea0d4
Create Date: 2023-12-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '4b53f1935d90'
down_revision = '83d0921ea0d4'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Добавляем поле name в таблицу users, если его нет
    if 'name' not in [column['name'] for column in inspector.get_columns('users')]:
        op.add_column('users', sa.Column('name', sa.String(length=100), nullable=True))
    
    # Добавляем поля в таблицу bookings, если их нет
    bookings_columns = [column['name'] for column in inspector.get_columns('bookings')]
    
    if 'number_of_guests' not in bookings_columns:
        op.add_column('bookings', sa.Column('number_of_guests', sa.Integer(), server_default='1', nullable=False))
    
    if 'user_id' not in bookings_columns:
        op.add_column('bookings', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Заполняем user_id первым пользователем
    op.execute('UPDATE bookings SET user_id = (SELECT id FROM users LIMIT 1) WHERE user_id IS NULL')
    
    # Для SQLite создаем foreign key через batch_alter_table
    with op.batch_alter_table('bookings') as batch_op:
        if 'fk_bookings_user_id' not in [fk['name'] for fk in inspector.get_foreign_keys('bookings')]:
            batch_op.create_foreign_key(
                'fk_bookings_user_id',
                'users',
                ['user_id'],
                ['id']
            )


def downgrade():
    with op.batch_alter_table('bookings') as batch_op:
        batch_op.drop_constraint('fk_bookings_user_id', type_='foreignkey')
    
    op.drop_column('bookings', 'user_id')
    op.drop_column('bookings', 'number_of_guests')
    op.drop_column('users', 'name')