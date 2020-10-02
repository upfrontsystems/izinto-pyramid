"""Add image to collection

Revision ID: 7133b9ab9aed
Revises: 48db96e003a1
Create Date: 2020-10-02 12:12:05.241164

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7133b9ab9aed'
down_revision = '48db96e003a1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('collection', sa.Column('image', sa.LargeBinary(), nullable=True))
    op.add_column('dashboard', sa.Column('image', sa.LargeBinary(), nullable=True))


def downgrade():
    op.drop_column('dashboard', 'image')
    op.drop_column('collection', 'image')
