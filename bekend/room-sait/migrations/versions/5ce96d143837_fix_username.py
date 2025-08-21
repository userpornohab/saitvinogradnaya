"""fix-username

Revision ID: 5ce96d143837
Revises: 4b53f1935d90
Create Date: 2023-12-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '5ce96d143837'
down_revision = '4b53f1935d90'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Проверяем, есть ли колонка name и является ли она nullable
    users_columns = {c['name']: c for c in inspector.get_columns('users')}
    if 'name' in users_columns:
        # Обновляем существующих пользователей
        op.execute("UPDATE users SET name = '' WHERE name IS NULL")
        
        # Для SQLite используем batch_alter_table для изменения колонки
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column(
                'name',
                existing_type=sa.String(length=100),
                nullable=False,
                server_default=''
            )
    else:
        # Если колонки нет, добавляем её
        op.add_column(
            'users',
            sa.Column('name', sa.String(length=100), nullable=False, server_default='')
        )


def downgrade():
    # В обратной миграции просто устанавливаем nullable=True
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column(
            'name',
            existing_type=sa.String(length=100),
            nullable=True,
            server_default=None
        )