"""Add branding model

Revision ID: 401d8bd935f0
Revises: 91cb3aee76c9
Create Date: 2021-02-16 14:54:09.736612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '401d8bd935f0'
down_revision = '91cb3aee76c9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('branding',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('hostname', sa.Unicode(
                        length=500), nullable=True),
                    sa.Column('favicon', sa.Unicode(
                        length=500), nullable=True),
                    sa.Column('logo', sa.Unicode(length=500), nullable=True),
                    sa.Column('logo_mobile', sa.Unicode(length=500), nullable=True),
                    sa.Column('banner', sa.Unicode(length=500), nullable=True),
                    sa.Column('user_id', sa.VARCHAR(
                        length=32), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['user.id'], ondelete='cascade'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('hostname')
                    )
    op.create_index(op.f('ix_branding_id'), 'branding', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_branding_id'), table_name='branding')
    op.drop_table('branding')
