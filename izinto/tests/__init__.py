from minimock import Mock
import unittest
import random
from pyramid import testing, registry
from sqlalchemy import engine_from_config, create_engine
import transaction
from izinto.models import (Base, initialize_sql, Role, Permission, PermissionRole, OTP, Dashboard, Collection,
                           UserDashboard, UserCollection)


def _init_testing_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = initialize_sql(engine)
    return session


def dummy_request(dbsession, **kwargs):
    return testing.DummyRequest(dbsession=dbsession, **kwargs)


class FakeRegistry(registry.Registry):
    """Fake the Registry used to lookup configuration values."""

    def __init__(self):
        super(FakeRegistry, self).__init__()
        self.settings = {
            'authentication.timeout': 86400,
            'izinto.app.secret': 'secret'}


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.session = _init_testing_db()
        self.config = testing.setUp(registry=FakeRegistry())
        self.config.include("pyramid_jinja2")
        self.config.include("pyramid_mailer.testing")
        self.config.include("pyramid_mailer.debug")

    def tearDown(self):
        """ tear down """
        testing.tearDown()
        transaction.abort()


def add_user(session, role='User', telephone=None, password='password', email='testuser@email.com', firstname='Test',
             confirmed_registration=True):
    """
    Adds a user for testing
    :param session:
    :param telephone:
    :param password:
    :param role:
    :param email:
    :param firstname:
    :param confirmed_registration:
    :return:
    """
    from izinto.models import Role, User

    if not telephone:
        telephone = random.randint(1, 10000)
    user = User(firstname=firstname,
                surname='User',
                telephone=telephone,
                address='1 Road',
                email=email,
                confirmed_registration=confirmed_registration)
    if password:
        user.set_password(password)

    session.add(user)
    session.flush()
    user_role = session.query(Role).filter(Role.name == role).first()
    if not user_role:
        user_role = Role(name=role)
        session.add(user_role)
        session.flush()
    user.roles.append(user_role)

    return user


def add_roles_and_permissions(session):
    """
    add test user roles and permissions. This may or may not
    be needed.
    :param session:
    :return:
    """
    session.bulk_insert_mappings(Role, [
        {'id': 1, 'name': 'Administrator'},
        {'id': 2, 'name': 'User'}
    ])

    session.bulk_insert_mappings(Permission, [
        {'id': 1, 'name': 'view'},
        {'id': 2, 'name': 'add'},
        {'id': 3, 'name': 'edit'},
        {'id': 4, 'name': 'delete'}
    ])

    session.bulk_insert_mappings(PermissionRole, [
        {'permission_id': 1, 'role_id': 1},
        {'permission_id': 2, 'role_id': 1},
        {'permission_id': 3, 'role_id': 1},
        {'permission_id': 4, 'role_id': 1},

        {'permission_id': 1, 'role_id': 2},
        {'permission_id': 2, 'role_id': 2},
        {'permission_id': 3, 'role_id': 2},
        {'permission_id': 4, 'role_id': 2},

        {'permission_id': 1, 'role_id': 3},
        {'permission_id': 2, 'role_id': 3},
        {'permission_id': 3, 'role_id': 3},
        {'permission_id': 4, 'role_id': 3},

    ])


def add_collection(session, title='Title', description='Description', users=[]):
    """
    Create dashboard for testins
    :param session:
    :param title:
    :param description:
    :param users:
    :return:
    """

    collection = Collection(title=title, description=description)
    session.add(collection)
    session.flush()

    for user in users:
        session.add(UserCollection(user_id=user.id, collection_id=collection.id))
    session.flush()

    return collection


def add_dashboard(session, title='Title', description='Description', collection_id=None, users=[]):
    """
    Create dashboard for testins
    :param session:
    :param title:
    :param description:
    :param collection_id:
    :param users:
    :return:
    """

    dashboard = Dashboard(title=title, description=description, collection_id=collection_id)
    session.add(dashboard)
    session.flush()

    for user in users:
        session.add(UserDashboard(user_id=user.id, dashboard_id=dashboard.id))
    session.flush()

    return dashboard


def mock_otp():
    """
    Mock the otp send functions
    :return:
    """
    OTP._send_email_otp = Mock('OTP._send_email_otp')
    OTP._send_cellphone_otp = Mock('OTP._send_cellphone_otp')
    OTP._send_email_otp.mock_returns = Mock(True)
    OTP._send_cellphone_otp.mock_returns = Mock(True)
