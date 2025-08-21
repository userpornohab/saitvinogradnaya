"""Add floor and site models

Revision ID: b05cec5bee32
Revises: d375ee6625d7
Create Date: 2025-07-27 19:53:39.106379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b05cec5bee32'
down_revision = 'd375ee6625d7'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле floor
    op.add_column('rooms', sa.Column('floor', sa.Integer(), nullable=True))
    
    # Проверяем существование таблиц перед созданием
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()
    
    if 'site_info' not in tables:
        op.create_table('site_info',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('main_photo', sa.String(length=200), nullable=True),
            sa.Column('main_description', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.execute("INSERT INTO site_info (id) VALUES (1)")
    
    if 'courtyard_photos' not in tables:
        op.create_table('courtyard_photos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('url', sa.String(length=200), nullable=False),
            sa.Column('site_info_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['site_info_id'], ['site_info.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    if 'testimonials' not in tables:
        op.create_table('testimonials',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('author_name', sa.String(length=100), nullable=False),
            sa.Column('author_icon_url', sa.String(length=200), nullable=False),
            sa.Column('comment', sa.Text(), nullable=False),
            sa.Column('site_info_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['site_info_id'], ['site_info.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    if 'faqs' not in tables:
        op.create_table('faqs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('question', sa.Text(), nullable=False),
            sa.Column('answer', sa.Text(), nullable=False),
            sa.Column('site_info_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['site_info_id'], ['site_info.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    op.drop_table('faqs')
    op.drop_table('testimonials')
    op.drop_table('courtyard_photos')
    op.drop_table('site_info')
    op.drop_column('rooms', 'floor')