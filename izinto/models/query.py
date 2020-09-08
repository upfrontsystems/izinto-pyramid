from sqlalchemy import (Column, Unicode, Integer, ForeignKey, TEXT, UniqueConstraint)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Query(Base):
    """
    Dashboard query Model
    """

    __tablename__ = 'query'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode(length=100))
    query = Column(TEXT)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete='CASCADE'), nullable=False)
    data_source_id = Column(Integer, ForeignKey('data_source.id'), nullable=False)

    dashboard = relationship('Dashboard', backref='queries')
    data_source = relationship('DataSource')

    __table_args__ = (UniqueConstraint('name', 'dashboard_id'),)

    def as_dict(self):
        return {'id': self.id,
                'name': self.name,
                'query': self.query,
                'dashboard_id': self.dashboard_id,
                'data_source_id': self.data_source_id,
                'data_source': self.data_source.as_dict()}

    def __repr__(self):
        return 'Query<name: %s>' % self.name
