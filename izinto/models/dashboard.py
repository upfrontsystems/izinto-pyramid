from sqlalchemy import (Column, Unicode, Integer, ForeignKey, TEXT, VARCHAR)
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
    content = Column(TEXT)
    # a dashboard can be an 'old' or a 'new' type dashboard
    # new type dashboards are html documents stored in `content`
    type = Column(VARCHAR, nullable=False, default='new')
    index = Column(Integer, default=1)

    collections = relationship('Collection')
    users = relationship('User', secondary="user_dashboard", backref='dashboards')
    variables = relationship('Variable')

    def as_dict(self):

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'collection_id': self.collection_id,
                'index': self.index,
                'type': self.type,
                'content': self.content,
                'users': [user.as_dict() for user in self.users],
                'variables': [var.as_dict() for var in self.variables]}

    def __repr__(self):
        return 'Dashboard<title: %s>' % self.title
