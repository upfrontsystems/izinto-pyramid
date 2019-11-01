import argparse
import sys
import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config
from sqlalchemy.exc import OperationalError
from izinto.security import Administrator, all_roles, all_permissions

from izinto.models import User, Role, Permission, PermissionRole, initialize_sql


def setup_models(session):
    """
    Add or update models / fixtures in the database.

    """

    for permission in all_permissions:
        session.add(Permission(name=permission))

    for role in all_roles:
        session.add(Role(name=role))

    session.flush()
    for permission in session.query(Permission).all():
        for role in session.query(Role).all():
            session.add(PermissionRole(role_id=role.id, permission_id=permission.id))

    session.flush()
    admin = User(firstname='Admin', surname='Admin', email='admin@izinto.net', confirmed_registration=True)
    session.add(admin)
    admin_role = session.query(Role).filter(Role.name == Administrator).first()
    admin.roles.append(admin_role)
    admin.set_password('admin')

    transaction.commit()


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    settings = get_appsettings(args.config_uri, options={})
    engine = engine_from_config(settings, 'sqlalchemy.')
    session = initialize_sql(engine)

    try:
        setup_models(session)
    except OperationalError:
        print('''
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for description and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.
            ''')
