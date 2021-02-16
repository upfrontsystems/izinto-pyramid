"""Add branding model

Revision ID: c505d398df5a
Revises: 91cb3aee76c9
Create Date: 2021-02-15 20:54:06.306085

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c505d398df5a'
down_revision = '91cb3aee76c9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('branding',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('hostname', sa.Unicode(length=500), nullable=True),
                    sa.Column('favicon', sa.Unicode(length=500), nullable=True),
                    sa.Column('logo', sa.Unicode(length=500), nullable=True),
                    sa.Column('banner', sa.Unicode(length=500), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_branding_id'), 'branding', ['id'], unique=False)

    # add default branding for izinto
    conn = op.get_bind()
    conn.execute("insert into branding (hostname) values ('izinto')")


def downgrade():
    op.drop_index(op.f('ix_branding_id'), table_name='branding')
    op.drop_table('branding')
