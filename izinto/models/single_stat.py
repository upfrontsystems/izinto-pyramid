from sqlalchemy import (Column, ForeignKey, Unicode, Integer, VARCHAR)
from sqlalchemy.orm import relationship
from izinto.models import Base


class SingleStat(Base):
    """
    Single stat Model
    """

    __tablename__ = 'single_stat'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Unicode(length=200))
    query = Column(VARCHAR)
    decimals = Column(Integer, default=0)
    format = Column(Unicode(length=100), default='')
    thresholds = Column(VARCHAR, default='')
    colors = Column(VARCHAR, default='')
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete='CASCADE'), nullable=False)
    data_source_id = Column(Integer, ForeignKey('data_source.id'))

    dashboard = relationship('Dashboard')
    data_source = relationship('DataSource')

    def as_dict(self):

        return {'id': self.id,
                'title': self.title,
                'query': self.query,
                'decimals': self.decimals,
                'format': self.format,
                'thresholds': self.thresholds,
                'colors': self.colors,
                'dashboard_id': self.dashboard_id,
                'data_source_id': self.data_source_id}

    def __repr__(self):
        return 'SingleStat<id: %s, title: %s>' % (self.id, self.title)
