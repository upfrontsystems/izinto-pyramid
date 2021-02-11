"""Add owner to data source

Revision ID: 65a1f6116bc8
Revises: c900e525669c
Create Date: 2021-02-11 12:23:13.854115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65a1f6116bc8'
down_revision = 'c900e525669c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_source', sa.Column('owner_id', sa.VARCHAR(length=32), nullable=True))
    # make admin owner of existing data sources
    conn = op.get_bind()
    admin = conn.execute(
        "select * from \"user\" where email = 'admin@izinto.cloud'").first()
    conn.execute("update data_source set owner_id = '%s'" % admin.id)

    op.alter_column('data_source', 'owner_id',existing_type=sa.VARCHAR(length=32), nullable=False)
    op.create_foreign_key('fk_data_source_owner_id', 'data_source', 'user', ['owner_id'], ['id'], ondelete='cascade')


def downgrade():
    op.drop_constraint('fk_data_source_owner_id', 'data_source', type_='foreignkey')
    op.drop_column('data_source', 'owner_id')
