"""init

Revision ID: 788f9a487d85
Revises: 
Create Date: 2019-10-29 14:48:14.539473

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '788f9a487d85'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('permission',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_permission')),
                    sa.UniqueConstraint('name', name=op.f('uq_permission_name'))
                    )
    op.create_table('role',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_role'))
                    )
    op.create_table('user',
                    sa.Column('id', sa.VARCHAR(length=32), nullable=False),
                    sa.Column('firstname', sa.Unicode(length=100), nullable=False),
                    sa.Column('surname', sa.Unicode(length=100), nullable=False),
                    sa.Column('telephone', sa.Unicode(length=100), nullable=True),
                    sa.Column('address', sa.VARCHAR(), nullable=True),
                    sa.Column('password', sa.Unicode(length=100), nullable=True),
                    sa.Column('salt', sa.Unicode(length=100), nullable=True),
                    sa.Column('email', sa.Unicode(length=255), nullable=True),
                    sa.Column('confirmed_registration', sa.Boolean(), nullable=False),
                    sa.Column('inactive', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_user'))
                    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_telephone'), 'user', ['telephone'], unique=False)
    op.create_table('otp_table',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('identifier', sa.Text(), nullable=True),
                    sa.Column('otp', sa.Text(), nullable=True),
                    sa.Column('secret', sa.Text(), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.Column('user_id', sa.VARCHAR(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_otp_table_user_id_user'),
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_otp_table'))
                    )
    op.create_table('permission_role',
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.Column('permission_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['permission_id'], ['permission.id'],
                                            name=op.f('fk_permission_role_permission_id_permission')),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name=op.f('fk_permission_role_role_id_role')),
                    sa.PrimaryKeyConstraint('role_id', 'permission_id', name=op.f('pk_permission_role'))
                    )
    op.create_table('user_role',
                    sa.Column('user_id', sa.VARCHAR(length=32), nullable=False),
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name=op.f('fk_user_role_role_id_role')),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_role_user_id_user')),
                    sa.PrimaryKeyConstraint('user_id', 'role_id', name=op.f('pk_user_role'))
                    )


def downgrade():
    op.drop_table('user_role')
    op.drop_table('permission_role')
    op.drop_table('otp_table')
    op.drop_index(op.f('ix_user_telephone'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('role')
    op.drop_table('permission')
