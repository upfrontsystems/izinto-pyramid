"""Add collection model

Revision ID: 6f25480d827e
Revises: 31e1b48ff8dd
Create Date: 2019-11-19 20:52:05.079085

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6f25480d827e'
down_revision = '31e1b48ff8dd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('collection',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.Unicode(length=100), nullable=True),
                    sa.Column('description', sa.Unicode(length=500), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_collection_id'), 'collection', ['id'], unique=False)
    op.create_table('dashboard_collection',
                    sa.Column('dashboard_id', sa.Integer(), nullable=False),
                    sa.Column('collection_id', sa.Integer(), nullable=False),
                    sa.Column('order', sa.Integer(), autoincrement=True, nullable=True),
                    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ),
                    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'], ),
                    sa.PrimaryKeyConstraint('dashboard_id', 'collection_id')
                    )
    op.create_table('user_collection',
                    sa.Column('user_id', sa.VARCHAR(length=32), nullable=False),
                    sa.Column('collection_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('user_id', 'collection_id')
                    )
    op.create_table('user_dashboard',
                    sa.Column('user_id', sa.VARCHAR(length=32), nullable=False),
                    sa.Column('dashboard_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['dashboard_id'], ['dashboard.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('user_id', 'dashboard_id')
                    )

    conn = op.get_bind()
    # copy users from user_id to user_dashboard
    for dashboard in conn.execute("select * from dashboard"):
        conn.execute("insert into user_dashboard (user_id, dashboard_id) values ('%s', %s)" %
                     (dashboard.user_id, dashboard.id))

    op.drop_constraint('fk_dashboard_user_id_user', 'dashboard', type_='foreignkey')
    op.drop_column('dashboard', 'user_id')


def downgrade():
    op.add_column('dashboard', sa.Column('user_id', sa.VARCHAR(length=32), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_dashboard_user_id_user', 'dashboard', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_table('user_dashboard')
    op.drop_table('user_collection')
    op.drop_table('dashboard_collection')
    op.drop_index(op.f('ix_collection_id'), table_name='collection')
    op.drop_table('collection')
