"""Add variables

Revision ID: 31e1b48ff8dd
Revises: 0fe74df52a92
Create Date: 2019-11-18 13:54:03.870259

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '31e1b48ff8dd'
down_revision = '0fe74df52a92'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('variable',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=100), nullable=True),
                    sa.Column('value', sa.Unicode(length=100), nullable=True),
                    sa.Column('dashboard_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('value', 'dashboard_id')
                    )
    op.create_index(op.f('ix_variable_id'), 'variable', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_variable_id'), table_name='variable')
    op.drop_table('variable')
