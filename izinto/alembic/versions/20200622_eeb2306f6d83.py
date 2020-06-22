"""Add year dashboard view

Revision ID: eeb2306f6d83
Revises: bc9f4fa39936
Create Date: 2020-06-22 20:21:53.909258

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'eeb2306f6d83'
down_revision = 'bc9f4fa39936'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("insert into dashboard_view (name, icon) values ('%s', '%s');" % ('Year', 'view_stream'))

    for chart in conn.execute("select * from chart;"):
        view = conn.execute("select * from dashboard_view where name = 'Year'").first()
        conn.execute("insert into chart_group_by (chart_id, dashboard_view_id, value) "
                     "values (%s, %s, '%s')" % (chart.id, view.id, 'auto'))


def downgrade():
    pass
