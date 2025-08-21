"""fix-pricet

Revision ID: 23f3dcaa934d
Revises: ddf751140e57
Create Date: 2025-06-05 03:00:17.762413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '23f3dcaa934d'
down_revision: Union[str, None] = 'ddf751140e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Для SQLite требуется специальная обработка
    conn = op.get_bind()
    if conn.dialect.name == 'sqlite':
        # SQLite не поддерживает ALTER TABLE с изменением NULLABLE напрямую
        # Создаем временную таблицу
        op.create_table(
            'bookings_temp',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('room_id', sa.Integer),
            sa.Column('check_in_date', sa.Date),
            sa.Column('check_out_date', sa.Date),
            sa.Column('number_of_guests', sa.Integer),
            sa.Column('price', sa.Float, nullable=False),
            sa.Column('user_id', sa.Integer)
        )
        
        # Копируем данные из старой таблицы
        op.execute("""
            INSERT INTO bookings_temp (id, room_id, check_in_date, check_out_date, number_of_guests, price, user_id)
            SELECT id, room_id, check_in_date, check_out_date, number_of_guests, COALESCE(price, 0.0), user_id 
            FROM bookings
        """)
        
        # Удаляем старую таблицу
        op.drop_table('bookings')
        
        # Переименовываем временную таблицу
        op.rename_table('bookings_temp', 'bookings')
    else:
        # Для других СУБД используем стандартный подход
        op.add_column('bookings', sa.Column('price', sa.Float(), nullable=True))
        op.execute("UPDATE bookings SET price = 0.0 WHERE price IS NULL")
        op.alter_column('bookings', 'price', nullable=False)

def downgrade():
    # Для SQLite требуется специальная обработка
    conn = op.get_bind()
    if conn.dialect.name == 'sqlite':
        # Создаем временную таблицу без колонки price
        op.create_table(
            'bookings_temp',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('room_id', sa.Integer),
            sa.Column('check_in_date', sa.Date),
            sa.Column('check_out_date', sa.Date),
            sa.Column('number_of_guests', sa.Integer),
            sa.Column('user_id', sa.Integer)
        )
        
        # Копируем данные
        op.execute("""
            INSERT INTO bookings_temp (id, room_id, check_in_date, check_out_date, number_of_guests, user_id)
            SELECT id, room_id, check_in_date, check_out_date, number_of_guests, user_id 
            FROM bookings
        """)
        
        # Удаляем старую таблицу
        op.drop_table('bookings')
        
        # Переименовываем временную таблицу
        op.rename_table('bookings_temp', 'bookings')
    else:
        # Для других СУБД
        op.drop_column('bookings', 'price')