"""Add Query model

Revision ID: 2e402e4100cf
Revises: e8b34e96585e
Create Date: 2020-09-04 10:04:39.932369

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2e402e4100cf'
down_revision = 'e8b34e96585e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('query',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=100), nullable=True),
                    sa.Column('query', sa.TEXT(), nullable=True),
                    sa.Column('user_id', sa.VARCHAR(length=32), nullable=False),
                    sa.Column('data_source_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['data_source_id'], ['data_source.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name', 'user_id')
                    )
    op.create_index(op.f('ix_query_id'), 'query', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_query_id'), table_name='query')
    op.drop_table('query')
