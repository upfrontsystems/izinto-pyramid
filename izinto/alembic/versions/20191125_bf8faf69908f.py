"""Fix cascades

Revision ID: bf8faf69908f
Revises: 0dcd57b4c430
Create Date: 2019-11-25 13:46:22.604253

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bf8faf69908f'
down_revision = '0dcd57b4c430'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('user_collection_collection_id_fkey', 'user_collection', type_='foreignkey')
    op.drop_constraint('user_collection_user_id_fkey', 'user_collection', type_='foreignkey')
    op.create_foreign_key('user_collection_user_id_fkey', 'user_collection', 'user', ['user_id'], ['id'],
                          ondelete='cascade')
    op.create_foreign_key('user_collection_collection_id_fkey', 'user_collection', 'collection', ['collection_id'],
                          ['id'], ondelete='cascade')

    op.drop_constraint('user_dashboard_user_id_fkey', 'user_dashboard', type_='foreignkey')
    op.drop_constraint('user_dashboard_dashboard_id_fkey', 'user_dashboard', type_='foreignkey')
    op.create_foreign_key('user_dashboard_dashboard_id_fkey', 'user_dashboard', 'dashboard', ['dashboard_id'], ['id'],
                          ondelete='cascade')
    op.create_foreign_key('user_dashboard_user_id_fkey', 'user_dashboard', 'user', ['user_id'], ['id'],
                          ondelete='cascade')

    op.drop_constraint('fk_user_role_user_id_user', 'user_role', type_='foreignkey')
    op.drop_constraint('fk_user_role_role_id_role', 'user_role', type_='foreignkey')
    op.create_foreign_key('fk_user_role_user_id_user', 'user_role', 'user', ['user_id'], ['id'], ondelete='cascade')
    op.create_foreign_key('fk_user_role_role_id_role', 'user_role', 'role', ['role_id'], ['id'], ondelete='cascade')


def downgrade():
    pass
