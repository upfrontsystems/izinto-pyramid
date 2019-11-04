"""Add dashboard and chart

Revision ID: 0fe74df52a92
Revises: 788f9a487d85
Create Date: 2019-11-01 15:01:54.950741

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0fe74df52a92'
down_revision = '788f9a487d85'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dashboard',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.Unicode(length=100), nullable=True),
                    sa.Column('description', sa.Unicode(length=500), nullable=True),
                    sa.Column('user_id', sa.VARCHAR(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_dashboard_user_id_user'),
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_dashboard'))
                    )
    op.create_index(op.f('ix_dashboard_id'), 'dashboard', ['id'], unique=False)

    op.create_table('chart',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('index', sa.Integer(), nullable=True),
                    sa.Column('selector', sa.Unicode(length=100), nullable=True),
                    sa.Column('title', sa.Unicode(length=100), nullable=False),
                    sa.Column('unit', sa.VARCHAR(), nullable=True),
                    sa.Column('color', sa.VARCHAR(), nullable=True),
                    sa.Column('type', sa.VARCHAR(), nullable=True),
                    sa.Column('group_by', sa.VARCHAR(), nullable=True),
                    sa.Column('query', sa.VARCHAR(), nullable=True),
                    sa.Column('dashboard_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'],
                                            name=op.f('fk_chart_dashboard_id_dashboard'), ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_chart'))
                    )
    op.create_index(op.f('ix_chart_id'), 'chart', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_chart_id'), table_name='chart')
    op.drop_table('chart')
    op.drop_index(op.f('ix_dashboard_id'), table_name='dashboard')
    op.drop_table('dashboard')
