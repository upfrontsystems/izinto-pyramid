"""Add role to user dashboard and collection

Revision ID: 555ab730233b
Revises: 7133b9ab9aed
Create Date: 2020-12-04 16:22:40.103894

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '555ab730233b'
down_revision = '7133b9ab9aed'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_collection', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('user_collection_role_id', 'user_collection', 'role', ['role_id'], ['id'])
    op.add_column('user_dashboard', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('user_dashboard_role_id', 'user_dashboard', 'role', ['role_id'], ['id'])

    conn = op.get_bind()
    # add admin role to all current mappings
    admin_role = conn.execute("select * from role where name = 'Administrator'").first()
    conn.execute("update user_collection set role_id = %s" % admin_role.id)
    conn.execute("update user_dashboard set role_id = %s" % admin_role.id)


def downgrade():
    op.drop_constraint('user_dashboard_role_id', 'user_dashboard', type_='foreignkey')
    op.drop_column('user_dashboard', 'role_id')
    op.drop_constraint('user_collection_role_id', 'user_collection', type_='foreignkey')
    op.drop_column('user_collection', 'role_id')
