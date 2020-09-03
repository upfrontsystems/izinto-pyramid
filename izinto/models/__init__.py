from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
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
from izinto.models.chart import Chart
from izinto.models.chart_group_by import ChartGroupBy
from izinto.models.collection import Collection
from izinto.models.dashboard import Dashboard
from izinto.models.dashboard_view import DashboardView
from izinto.models.data_source import DataSource
from izinto.models.otp import OTP
from izinto.models.permission import Permission
from izinto.models.permisson_role import PermissionRole
from izinto.models.query import Query
from izinto.models.role import Role
from izinto.models.single_stat import SingleStat
from izinto.models.user_role import UserRole
from izinto.models.user import User
from izinto.models.user_collection import UserCollection
from izinto.models.user_dashboard import UserDashboard
from izinto.models.variable import Variable
