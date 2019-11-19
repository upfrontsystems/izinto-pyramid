from sqlalchemy import (Column, Unicode, Integer)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Collection(Base):
    """
    A collection of dashboards
    """

    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Unicode(length=100))
    description = Column(Unicode(length=500))

    users = relationship('User', secondary="user_collection", backref="collections")
    dashboards = relationship('Dashboard', secondary="dashboard_collection", backref="collections")

    def as_dict(self):

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'users': [user.as_dict() for user in self.users],
                'dashboards': [dashboard.as_dict() for dashboard in self.dashboards]}

    def __repr__(self):
        return 'Collection<title: %s>' % self.title
