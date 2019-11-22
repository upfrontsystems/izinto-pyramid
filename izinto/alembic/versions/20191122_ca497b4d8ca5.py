"""Set variable unique constraint

Revision ID: ca497b4d8ca5
Revises: 6f25480d827e
Create Date: 2019-11-22 19:30:05.123127

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ca497b4d8ca5'
down_revision = '6f25480d827e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('dashboard_collection')
    op.drop_constraint('variable_value_dashboard_id_key', 'variable', type_='unique')
    op.create_unique_constraint('variable_name_dashboard_id_key', 'variable', ['name', 'dashboard_id'])


def downgrade():
    op.drop_constraint('variable_name_dashboard_id_key', 'variable', type_='unique')
    op.create_unique_constraint('variable_value_dashboard_id_key', 'variable', ['value', 'dashboard_id'])
    op.create_table('dashboard_collection',
                    sa.Column('dashboard_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('collection_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'],
                                            name='dashboard_collection_collection_id_fkey'),
                    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'],
                                            name='dashboard_collection_dashboard_id_fkey'),
                    sa.PrimaryKeyConstraint('dashboard_id', 'collection_id', name='dashboard_collection_pkey')
                    )
