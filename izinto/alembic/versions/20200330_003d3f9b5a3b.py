"""add labels, min, max and height to chart

Revision ID: 003d3f9b5a3b
Revises: c8575c7c2611
Create Date: 2020-03-30 15:43:02.751311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003d3f9b5a3b'
down_revision = 'c8575c7c2611'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('chart', sa.Column('height', sa.Integer(), nullable=True))
    op.add_column('chart', sa.Column('labels', sa.VARCHAR(), nullable=True))
    op.add_column('chart', sa.Column('max', sa.Integer(), nullable=True))
    op.add_column('chart', sa.Column('min', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('chart', 'min')
    op.drop_column('chart', 'max')
    op.drop_column('chart', 'labels')
    op.drop_column('chart', 'height')
