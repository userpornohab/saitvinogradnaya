"""update_booking_model_nullable

Revision ID: e08e886aa0e4
Revises: 3ea031bb080d
Create Date: 2025-06-24 00:24:55.144280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e08e886aa0e4'
down_revision = '3ea031bb080d'
branch_labels = None
depends_on = None

def upgrade():
    # Отключение проверки внешних ключей
    op.execute('PRAGMA foreign_keys=OFF;')
    
    try:
        # Создаем новую таблицу с нужной структурой
        op.create_table(
            'bookings_new',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('room_id', sa.Integer, sa.ForeignKey('rooms.id')),
            sa.Column('check_in_date', sa.Date, nullable=False),
            sa.Column('check_out_date', sa.Date, nullable=False),
            sa.Column('number_of_guests', sa.Integer, default=1),
            sa.Column('price', sa.Float, nullable=False),
            sa.Column('guest_name', sa.String(length=100), nullable=True),
            sa.Column('guest_phone', sa.String(length=20), nullable=True),
            sa.Column('guest_comment', sa.Text, nullable=True)
        )
        
        # Копируем данные из старой таблицы
        op.execute("""
            INSERT INTO bookings_new (id, room_id, check_in_date, check_out_date, 
                                     number_of_guests, price)
            SELECT id, room_id, check_in_date, check_out_date, 
                   number_of_guests, price
            FROM bookings
        """)
        
        # Удаляем старую таблицу
        op.drop_table('bookings')
        
        # Переименовываем новую таблицу
        op.rename_table('bookings_new', 'bookings')
        
    finally:
        # Включаем проверку внешних ключей обратно
        op.execute('PRAGMA foreign_keys=ON;')

def downgrade():
    # Отключение проверки внешних ключей
    op.execute('PRAGMA foreign_keys=OFF;')
    
    try:
        # Создаем временную таблицу со старой структурой
        op.create_table(
            'bookings_old',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('room_id', sa.Integer, sa.ForeignKey('rooms.id')),
            sa.Column('check_in_date', sa.Date, nullable=False),
            sa.Column('check_out_date', sa.Date, nullable=False),
            sa.Column('number_of_guests', sa.Integer, default=1),
            sa.Column('price', sa.Float, nullable=False),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
        )
        
        # Копируем данные обратно
        op.execute("""
            INSERT INTO bookings_old (id, room_id, check_in_date, check_out_date, 
                                     number_of_guests, price)
            SELECT id, room_id, check_in_date, check_out_date, 
                   number_of_guests, price
            FROM bookings
        """)
        
        # Удаляем новую таблицу
        op.drop_table('bookings')
        
        # Переименовываем старую таблицу
        op.rename_table('bookings_old', 'bookings')
        
    finally:
        # Включаем проверку внешних ключей обратно
        op.execute('PRAGMA foreign_keys=ON;')