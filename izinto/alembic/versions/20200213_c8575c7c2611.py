"""Add chart group by and dashboard view models

Revision ID: c8575c7c2611
Revises: 25994465d8a7
Create Date: 2020-02-13 18:25:43.159158

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c8575c7c2611'
down_revision = '25994465d8a7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dashboard_view',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=200), nullable=True),
                    sa.Column('icon', sa.Unicode(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_dashboard_view_id'), 'dashboard_view', ['id'], unique=False)
    op.create_table('chart_group_by',
                    sa.Column('chart_id', sa.Integer(), nullable=False),
                    sa.Column('dashboard_view_id', sa.Integer(), nullable=False),
                    sa.Column('value', sa.Unicode(length=100), nullable=True),
                    sa.ForeignKeyConstraint(['chart_id'], ['chart.id'], ondelete='cascade'),
                    sa.ForeignKeyConstraint(['dashboard_view_id'], ['dashboard_view.id'], ondelete='cascade'),
                    sa.PrimaryKeyConstraint('chart_id', 'dashboard_view_id')
                    )

    conn = op.get_bind()
    for view in [['Hour', 'view_agenda'],
                 ['Day', 'view_day'],
                 ['Week', 'view_week'],
                 ['Month', 'view_module']]:
        conn.execute("insert into dashboard_view (name, icon) values ('%s', '%s');" % (view[0], view[1]))

    for chart in conn.execute("select * from chart;"):
        for group in [['Hour', '10m'],
                      ['Day', '1h'],
                      ['Week', '1d'],
                      ['Month', '1d']]:
            view = conn.execute("select * from dashboard_view where name = '%s'" % group[0]).first()
            conn.execute("insert into chart_group_by (chart_id, dashboard_view_id, value) "
                         "values (%s, %s, '%s')" % (chart.id, view.id, group[1]))


def downgrade():
    op.drop_table('chart_group_by')
    op.drop_index(op.f('ix_dashboard_view_id'), table_name='dashboard_view')
    op.drop_table('dashboard_view')
