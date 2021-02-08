"""Refactor collection and dashboard to base class

Revision ID: c900e525669c
Revises: cee7bf91f750
Create Date: 2021-02-05 17:09:30.599306

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c900e525669c'
down_revision = 'cee7bf91f750'
branch_labels = None
depends_on = None


def upgrade():
    # create container base class for collections and dashboards
    op.create_table('container_base',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.Unicode(length=100), nullable=True),
                    sa.Column('description', sa.Unicode(
                        length=500), nullable=True),
                    sa.Column('image', sa.LargeBinary(), nullable=True),
                    sa.Column('polymorphic_type', sa.Unicode(
                        length=50), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    conn = op.get_bind()
    container_id = 1
    # copy collection to base
    for collection in conn.execute("select * from collection order by id"):
        conn.execute("insert into container_base (id, title, description, image, polymorphic_type)"
                     " values (%s, '%s', '%s', %s, 'collection')" % (
                         collection.id, collection.title, collection.description, collection.image
                     ))
        container_id = collection.id
    dashboard_id = conn.execute("select * from dashboard order by id DESC").first().id
    container_id = max(container_id, dashboard_id)

    op.drop_column('collection', 'image')
    op.drop_column('collection', 'title')
    op.drop_column('collection', 'description')
    op.create_index(op.f('ix_container_base_id'), 'container_base', ['id'], unique=False)
    op.create_foreign_key('fk_collection_container_id', 'collection', 'container_base', [
                          'id'], ['id'], ondelete='CASCADE')

    container_id += 1
    # copy dashboard to base
    # remove primary key and foreign key constraints
    op.drop_constraint('variable_name_dashboard_id_key', 'variable', type_='unique')
    op.drop_constraint('user_dashboard_pkey', 'user_dashboard', type_='primary')
    op.execute('ALTER TABLE dashboard DROP CONSTRAINT pk_dashboard CASCADE')
    for dashboard in conn.execute("select * from dashboard order by id"):
        old_id = dashboard.id
        conn.execute("insert into container_base (id, title, description, image, polymorphic_type)"
                     " values (%s, '%s', '%s', %s, 'dashboard')" % (
                         container_id, dashboard.title, dashboard.description, dashboard.image
                     ))
        # update id and foreign keys
        conn.execute("update dashboard set id = '%s' where id = %s" % (container_id, old_id))
        conn.execute("update chart set dashboard_id = '%s' where dashboard_id = %s" % (container_id, old_id))
        conn.execute("update query set dashboard_id = '%s' where dashboard_id = %s" % (container_id, old_id))
        conn.execute("update single_stat set dashboard_id = '%s' where dashboard_id = %s" % (container_id, old_id))
        conn.execute("update user_dashboard set dashboard_id = '%s' where dashboard_id = %s" % (container_id, old_id))
        conn.execute("update variable set dashboard_id = '%s' where dashboard_id = %s" % (container_id, old_id))
        container_id += 1

    op.drop_index('ix_dashboard_id', table_name='dashboard')
    op.drop_column('dashboard', 'image')
    op.drop_column('dashboard', 'title')
    op.drop_column('dashboard', 'description')

    # recreate primary key and foreign keys
    op.create_primary_key('pk_dashboard', 'dashboard', ['id'])
    op.create_primary_key('user_dashboard_pkey', 'user_dashboard', ['user_id', 'dashboard_id'])
    op.create_foreign_key('fk_chart_dashboard_id_dashboard', 'chart', 'dashboard', [
                          'dashboard_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('query_dashboard_id_fkey', 'query', 'dashboard', [
                          'dashboard_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('single_stat_dashboard_id_fkey', 'single_stat', 'dashboard', [
                          'dashboard_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_dashboard_dashboard_id_fkey', 'user_dashboard', 'dashboard', [
                          'dashboard_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_dashboard_container_id', 'dashboard', 'container_base', [
                          'id'], ['id'], ondelete='CASCADE')

    # rename variables dashboard_id column
    op.alter_column('variable', 'dashboard_id', existing_type=sa.INTEGER(), new_column_name='container_id')
    op.create_unique_constraint('variable_name_container_id_key', 'variable', ['name', 'container_id'])
    op.create_foreign_key('fk_variable_container_id', 'variable', 'container_base', [
                          'container_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # rename variables container_id column
    op.drop_constraint('fk_variable_container_id', 'variable', type_='foreignkey')
    op.drop_constraint('variable_name_container_id_key', 'variable', type_='unique')
    op.alter_column('variable', 'container_id', existing_type=sa.INTEGER(), new_column_name='dashboard_id')
    op.create_foreign_key('variable_dashboard_id_fkey', 'variable', 'dashboard', [
                        'dashboard_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('variable_name_dashboard_id_key', 'variable', [
                                'name', 'dashboard_id'])

    op.add_column('dashboard', sa.Column('description', sa.VARCHAR(
        length=500), autoincrement=False, nullable=True))
    op.add_column('dashboard', sa.Column('title', sa.VARCHAR(
        length=100), autoincrement=False, nullable=True))
    op.add_column('dashboard', sa.Column(
        'image', postgresql.BYTEA(), autoincrement=False, nullable=True))
    # set dashboard contraints
    op.drop_constraint('fk_dashboard_container_id', 'dashboard', type_='foreignkey')
    op.create_index('ix_dashboard_id', 'dashboard', ['id'], unique=False)

    conn = op.get_bind()
    # copy back to dashboard
    for dashboard in conn.execute("select * from dashboard"):
        container = conn.execute("select * from container_base where id  = %s" % dashboard.id).first()
        conn.execute("update dashboard set title = '%s', description = '%s', image = %s where id = %s;"
                     % (container.title, container.description, container.image, dashboard.id))

    # add collection columns
    op.add_column('collection', sa.Column('description', sa.VARCHAR(
        length=500), autoincrement=False, nullable=True))
    op.add_column('collection', sa.Column('title', sa.VARCHAR(
        length=100), autoincrement=False, nullable=True))
    op.add_column('collection', sa.Column(
        'image', postgresql.BYTEA(), autoincrement=False, nullable=True))

    # copy base to collection
    for collection in conn.execute("select * from collection"):
        container = conn.execute("select * from container_base where id  = %s" % collection.id).first()
        conn.execute("update collection set title = '%s', description = '%s', image = %s where id = %s;"
                     % (container.title, container.description, container.image, collection.id))

    op.drop_constraint('fk_collection_container_id', 'collection', type_='foreignkey')
    op.drop_index(op.f('ix_container_base_id'), table_name='container_base')
    op.drop_table('container_base')
