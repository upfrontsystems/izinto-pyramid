"""Add Edit and View role

Revision ID: cee7bf91f750
Revises: 555ab730233b
Create Date: 2020-12-08 19:30:37.999364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cee7bf91f750'
down_revision = '555ab730233b'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()

    # add edit role
    conn.execute("insert into role (name) values ('Edit')")
    edit_role = conn.execute("select * from role where name = 'Edit'").first()
    # add permissions to role
    edit_permission = conn.execute("select * from permission where name = 'edit'").first()
    view_permission = conn.execute("select * from permission where name = 'view'").first()
    conn.execute("insert into permission_role (role_id, permission_id) values (%s, %s)"
                 % (edit_role.id, edit_permission.id))
    conn.execute("insert into permission_role (role_id, permission_id) values (%s, %s)"
                 % (edit_role.id, view_permission.id))

    # add view role
    conn.execute("insert into role (name) values ('View')")
    view_role = conn.execute("select * from role where name = 'View'").first()
    # add permissions to role
    conn.execute("insert into permission_role (role_id, permission_id) values (%s, %s)"
                 % (view_role.id, view_permission.id))


def downgrade():
    conn = op.get_bind()
    edit_role = conn.execute("select * from role where name = 'Edit'").first()
    conn.execute("delete from user_collection where role_id = %s" % edit_role.id)
    conn.execute("delete from user_dashboard where role_id = %s" % edit_role.id)
    conn.execute("delete from permission_role where role_id = %s" % edit_role.id)
    conn.execute("delete from role where id = %s" % edit_role.id)

    view_role = conn.execute("select * from role where name = 'View'").first()
    conn.execute("delete from user_collection where role_id = %s" % view_role.id)
    conn.execute("delete from user_dashboard where role_id = %s" % view_role.id)
    conn.execute("delete from permission_role where role_id = %s" % view_role.id)
    conn.execute("delete from role where id = %s" % view_role.id)
