"""Remove selector field

Revision ID: 94ffd922543d
Revises: dac1e5b53912
Create Date: 2020-02-04 18:18:23.787169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94ffd922543d'
down_revision = 'dac1e5b53912'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint('uq_dashboard_id_selector', 'chart', type_='unique')
    op.drop_column('chart', 'selector')

def downgrade():
    op.add_column('chart', sa.Column('selector', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.create_unique_constraint('uq_dashboard_id_selector', 'chart', ['dashboard_id', 'selector'])
