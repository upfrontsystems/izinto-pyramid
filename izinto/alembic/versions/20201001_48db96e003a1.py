"""Add hide date selector to dashboard

Revision ID: 48db96e003a1
Revises: 3cc3157d57cc
Create Date: 2020-10-01 15:48:05.375040

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '48db96e003a1'
down_revision = '3cc3157d57cc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('dashboard', sa.Column('date_hidden', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('dashboard', 'date_hidden')
