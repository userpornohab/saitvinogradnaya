"""fix-gust

Revision ID: ddf751140e57
Revises: 5ce96d143837
Create Date: 2023-12-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'ddf751140e57'
down_revision = '5ce96d143837'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Получаем информацию о колонке number_of_guests
    bookings_columns = {c['name']: c for c in inspector.get_columns('bookings')}
    
    if 'number_of_guests' in bookings_columns:
        # Обновляем записи с NULL значением
        op.execute("UPDATE bookings SET number_of_guests = 1 WHERE number_of_guests IS NULL")
        
        # Используем batch_alter_table для изменения колонки
        with op.batch_alter_table('bookings') as batch_op:
            batch_op.alter_column(
                'number_of_guests',
                existing_type=sa.INTEGER(),
                nullable=False,
                server_default='1'
            )


def downgrade():
    # В обратной миграции просто разрешаем NULL
    with op.batch_alter_table('bookings') as batch_op:
        batch_op.alter_column(
            'number_of_guests',
            existing_type=sa.INTEGER(),
            nullable=True,
            server_default=None
        )