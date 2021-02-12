"""Add request config text to datasource

Revision ID: 91cb3aee76c9
Revises: 65a1f6116bc8
Create Date: 2021-02-11 16:09:05.821241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91cb3aee76c9'
down_revision = '65a1f6116bc8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_source', sa.Column(
        'request', sa.TEXT(), nullable=True))


def downgrade():
    op.drop_column('data_source', 'request')
