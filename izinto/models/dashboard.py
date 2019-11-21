from sqlalchemy import (Column, Unicode, Integer, ForeignKey)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Dashboard(Base):
    """
    Dashboard Model
    """

    __tablename__ = 'dashboard'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Unicode(length=100))
    description = Column(Unicode(length=500))
    collection_id = Column(Integer, ForeignKey('collection.id', ondelete='CASCADE'), nullable=True)

    collections  = relationship('Collection')
    users = relationship('User', secondary="user_dashboard", backref='dashboards')
    variables = relationship('Variable')

    def as_dict(self):

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'collection_id': self.collection_id,
                'users': [user.as_dict() for user in self.users],
                'variables': [var.as_dict() for var in self.variables]}

    def __repr__(self):
        return 'Dashboard<title: %s>' % self.title
