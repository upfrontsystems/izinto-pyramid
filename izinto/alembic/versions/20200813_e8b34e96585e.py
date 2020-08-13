"""Add content to dashboard and drop script

Revision ID: e8b34e96585e
Revises: eeb2306f6d83
Create Date: 2020-08-13 19:03:06.583643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8b34e96585e'
down_revision = 'eeb2306f6d83'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_script_id', table_name='script')
    op.drop_table('script')
    op.add_column('dashboard', sa.Column('content', sa.TEXT(), nullable=True))
    op.add_column('dashboard', sa.Column('type', sa.VARCHAR(), nullable=False))


def downgrade():
    op.drop_column('dashboard', 'type')
    op.drop_column('dashboard', 'content')
    op.create_table('script',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('index', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('dashboard_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'], name='script_dashboard_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='script_pkey')
    )
    op.create_index('ix_script_id', 'script', ['id'], unique=False)
