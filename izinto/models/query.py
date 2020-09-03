from sqlalchemy import (Column, Unicode, Integer, ForeignKey, TEXT, VARCHAR)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Query(Base):
    """
    User query Model
    """

    __tablename__ = 'query'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode(length=100), unique=True)
    query = Column(TEXT)
    user_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    data_source_id = Column(Integer, ForeignKey('data_source.id'), nullable=False)

    user = relationship('User', backref='query')
    data_source = relationship('DataSource')

    def as_dict(self):
        return {'id': self.id,
                'name': self.name,
                'query': self.query,
                'user_id': self.user_id,
                'data_source_id': self.data_source_id}

    def __repr__(self):
        return 'Query<name: %s>' % self.name
