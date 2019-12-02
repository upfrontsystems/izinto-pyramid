"""Add datasource to single stat

Revision ID: 9d9f9b3e98ba
Revises: a58311284f39
Create Date: 2019-12-02 15:39:58.501837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d9f9b3e98ba'
down_revision = 'a58311284f39'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('single_stat', sa.Column('data_source_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_single_stat_data_source_id', 'single_stat', 'data_source', ['data_source_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_single_stat_data_source_id', 'single_stat', type_='foreignkey')
    op.drop_column('single_stat', 'data_source_id')
