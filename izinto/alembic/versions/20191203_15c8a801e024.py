"""Data source id not nullable

Revision ID: 15c8a801e024
Revises: 9d9f9b3e98ba
Create Date: 2019-12-03 10:38:09.292483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15c8a801e024'
down_revision = '9d9f9b3e98ba'
branch_labels = None
depends_on = None


def upgrade():
    # set default data source on existing charts
    conn = op.get_bind()
    data_source_id = 1
    data_source = conn.execute("SELECT * from data_source").first()
    if data_source:
        data_source_id = data_source.id
    else:
        conn.execute("INSERT into data_source (id, name) values (1, 'TEMP_DATA_SOURCE')")

    for chart in conn.execute("select * from chart where data_source_id is NULL"):
        conn.execute("update chart set data_source_id = '%s' where id = %s" % (data_source_id, chart.id))
    for stat in conn.execute("select * from single_stat where data_source_id is NULL"):
        conn.execute("update single_stat set data_source_id = '%s' where id = %s" % (data_source_id, stat.id))

    op.alter_column('chart', 'data_source_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('single_stat', 'data_source_id', existing_type=sa.INTEGER(), nullable=False)


def downgrade():
    op.alter_column('single_stat', 'data_source_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('chart', 'data_source_id', existing_type=sa.INTEGER(), nullable=True)
