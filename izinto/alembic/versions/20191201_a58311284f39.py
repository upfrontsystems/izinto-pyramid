"""Add data source

Revision ID: a58311284f39
Revises: c489fe4963dd
Create Date: 2019-12-01 22:05:44.640840

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a58311284f39'
down_revision = 'c489fe4963dd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('data_source',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=200), nullable=True),
                    sa.Column('type', sa.Unicode(length=100), nullable=True),
                    sa.Column('url', sa.Unicode(length=200), nullable=True),
                    sa.Column('username', sa.Unicode(length=100), nullable=True),
                    sa.Column('password', sa.Unicode(length=100), nullable=True),
                    sa.Column('database', sa.Unicode(length=200), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_data_source_id'), 'data_source', ['id'], unique=False)
    op.add_column('chart', sa.Column('data_source_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_chart_data_source_id', 'chart', 'data_source', ['data_source_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_chart_data_source_id', 'chart', type_='foreignkey')
    op.drop_column('chart', 'data_source_id')
    op.drop_index(op.f('ix_data_source_id'), table_name='data_source')
    op.drop_table('data_source')
