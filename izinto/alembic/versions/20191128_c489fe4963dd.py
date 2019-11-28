"""Add format to single stat

Revision ID: c489fe4963dd
Revises: 15f7b20b5dfe
Create Date: 2019-11-28 11:25:57.458156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c489fe4963dd'
down_revision = '15f7b20b5dfe'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('single_stat', sa.Column('format', sa.Unicode(length=100), nullable=True))

def downgrade():
    op.drop_column('single_stat', 'format')
