"""Add order to dashboard

Revision ID: 0dcd57b4c430
Revises: ca497b4d8ca5
Create Date: 2019-11-22 20:55:34.035959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dcd57b4c430'
down_revision = 'ca497b4d8ca5'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('dashboard', sa.Column('order', sa.Integer(), autoincrement=True, nullable=True))
    conn = op.get_bind()

    for ix, dashboard in enumerate(conn.execute("select * from dashboard")):
        conn.execute('update dashboard set "order" = %s where id = %s' % (ix, dashboard.id))


def downgrade():
    op.drop_column('dashboard', 'order')
