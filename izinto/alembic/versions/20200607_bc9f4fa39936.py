"""Rename dashboard order to index

Revision ID: bc9f4fa39936
Revises: 9c3fdaf55cf0
Create Date: 2020-06-07 19:17:03.270078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc9f4fa39936'
down_revision = '9c3fdaf55cf0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('dashboard', 'order', nullable=True, existing_type=sa.Integer(), new_column_name='index')


def downgrade():
    op.alter_column('dashboard', 'index', nullable=True, existing_type=sa.Integer(), new_column_name='order')
