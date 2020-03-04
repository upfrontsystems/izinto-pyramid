"""Remove group by from chart

Revision ID: 25994465d8a7
Revises: 9a1cf39d333a
Create Date: 2020-02-12 22:07:15.005851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25994465d8a7'
down_revision = '9a1cf39d333a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('chart', 'group_by')


def downgrade():
    op.add_column('chart', sa.Column('group_by', sa.VARCHAR(), autoincrement=False, nullable=True))
