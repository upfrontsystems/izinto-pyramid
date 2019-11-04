import unittest
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from pyramid import testing

import transaction


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        settings = self.config.get_settings()

        from izinto.models import initialize_sql

        self.engine = engine_from_config(settings, 'sqlalchemy.')
        self.session = initialize_sql(self.engine)

    def init_database(self):
        from izinto.models import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from izinto.models import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)
