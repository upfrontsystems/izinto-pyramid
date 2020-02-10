from sqlalchemy import (Column, ForeignKey, VARCHAR, Unicode, Integer, UniqueConstraint)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Chart(Base):
    """
    Chart Model
    """

    __tablename__ = 'chart'

    id = Column(Integer, primary_key=True, index=True)
    index = Column(Integer)
    title = Column(Unicode(length=100), nullable=False)
    unit = Column(VARCHAR)
    color = Column(VARCHAR)
    type = Column(VARCHAR)
    group_by = Column(VARCHAR)
    query = Column(VARCHAR)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete='CASCADE'))
    data_source_id = Column(Integer, ForeignKey('data_source.id'), nullable=False)
    decimals = Column(Integer, default=2)

    dashboard = relationship('Dashboard')
    data_source = relationship('DataSource')

    def as_dict(self):
        return {'id': self.id,
                'dashboard_id': self.dashboard_id,
                'index': self.index,
                'title': self.title,
                'unit': self.unit,
                'color': self.color,
                'type': self.type,
                'group_by': self.group_by,
                'query': self.query,
                'data_source_id': self.data_source_id,
                'decimals': self.decimals,
                'data_source': self.data_source.as_dict()}

    def __repr__(self):
        return "Chart<id: %s, title: '%s'>" % (self.id, self.title)
