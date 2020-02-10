"""Add decimals to chart

Revision ID: 9a1cf39d333a
Revises: 94ffd922543d
Create Date: 2020-02-10 16:00:50.258350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a1cf39d333a'
down_revision = '94ffd922543d'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('chart', sa.Column('decimals', sa.Integer(), nullable=True))
    conn = op.get_bind()
    conn.execute("update chart set decimals=2")

def downgrade():
    op.drop_column('chart', 'decimals')
