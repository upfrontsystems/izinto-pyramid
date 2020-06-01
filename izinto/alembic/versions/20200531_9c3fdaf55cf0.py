"""Add script model

Revision ID: 9c3fdaf55cf0
Revises: 003d3f9b5a3b
Create Date: 2020-05-31 16:35:02.644916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c3fdaf55cf0'
down_revision = '003d3f9b5a3b'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('script',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('index', sa.Integer(), nullable=True),
    sa.Column('title', sa.Unicode(length=100), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=True),
    sa.Column('dashboard_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_script_id'), 'script', ['id'], unique=False)
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_script_id'), table_name='script')
    op.drop_table('script')
    # ### end Alembic commands ###
