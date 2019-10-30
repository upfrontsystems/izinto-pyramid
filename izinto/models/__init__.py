from sqlalchemy.orm import configure_mappers, scoped_session, sessionmaker
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
import zope.sqlalchemy


session = scoped_session(sessionmaker(extension=zope.sqlalchemy.ZopeTransactionExtension()))
Base = declarative_base()


def includeme(config):
    """Call this function if this app is included in pyramid.includes."""
    settings = config.get_settings()
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)


def initialize_sql(engine):
    """ Start the session with the given engine and build the base """
    session.configure(bind=engine)
    Base.metadata.bind = engine

    return session


# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from izinto.models.role import Role
from izinto.models.user_role import UserRole
from izinto.models.user import User  # flake8: noqa
from izinto.models.otp import OTP
from izinto.models.permission import Permission
from izinto.models.permisson_role import PermissionRole

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession
