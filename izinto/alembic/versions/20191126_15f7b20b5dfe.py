"""Add single stat model

Revision ID: 15f7b20b5dfe
Revises: bf8faf69908f
Create Date: 2019-11-26 16:05:06.324613

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '15f7b20b5dfe'
down_revision = 'bf8faf69908f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('single_stat',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.Unicode(length=200), nullable=True),
                    sa.Column('query', sa.VARCHAR(), nullable=True),
                    sa.Column('decimals', sa.Integer(), nullable=True),
                    sa.Column('thresholds', sa.VARCHAR(), nullable=True),
                    sa.Column('colors', sa.VARCHAR(), nullable=True),
                    sa.Column('dashboard_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_single_stat_id'), 'single_stat', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_single_stat_id'), table_name='single_stat')
    op.drop_table('single_stat')
