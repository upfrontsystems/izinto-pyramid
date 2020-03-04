"""Chart selector unique

Revision ID: dac1e5b53912
Revises: 15c8a801e024
Create Date: 2020-01-31 17:13:56.134303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dac1e5b53912'
down_revision = '15c8a801e024'
branch_labels = None
depends_on = None

def upgrade():
    op.create_unique_constraint('uq_dashboard_id_selector', 'chart', ['dashboard_id', 'selector'])

def downgrade():
    op.drop_constraint('uq_dashboard_id_selector', 'chart', type_='unique')
