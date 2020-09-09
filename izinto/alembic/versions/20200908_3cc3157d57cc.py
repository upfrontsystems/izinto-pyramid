"""Replace user with dashboard in query

Revision ID: 3cc3157d57cc
Revises: 2e402e4100cf
Create Date: 2020-09-08 13:52:27.154609

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3cc3157d57cc'
down_revision = '2e402e4100cf'
branch_labels = None
depends_on = None


def upgrade():

    # delete all existing queries
    conn = op.get_bind()
    conn.execute("delete from query")

    op.add_column('query', sa.Column('dashboard_id', sa.Integer(), nullable=False))
    op.drop_constraint('query_name_user_id_key', 'query', type_='unique')
    op.create_unique_constraint('query_name_dashboard_id_key', 'query', ['name', 'dashboard_id'])
    op.drop_constraint('query_user_id_fkey', 'query', type_='foreignkey')
    op.create_foreign_key('query_dashboard_id_fkey', 'query', 'dashboard', ['dashboard_id'], ['id'], ondelete='CASCADE')
    op.drop_column('query', 'user_id')


def downgrade():

    # delete all existing queries
    conn = op.get_bind()
    conn.execute("delete from query")

    op.add_column('query', sa.Column('user_id', sa.VARCHAR(length=32), autoincrement=False, nullable=False))
    op.drop_constraint('query_dashboard_id_fkey', 'query', type_='foreignkey')
    op.create_foreign_key('query_user_id_fkey', 'query', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('query_name_dashboard_id_key', 'query', type_='unique')
    op.create_unique_constraint('query_name_user_id_key', 'query', ['name', 'user_id'])
    op.drop_column('query', 'dashboard_id')
