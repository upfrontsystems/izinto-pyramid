from sqlalchemy import (Column, ForeignKey, VARCHAR, Unicode, Integer)
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
    query = Column(VARCHAR)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete='CASCADE'))
    data_source_id = Column(Integer, ForeignKey('data_source.id'), nullable=False)
    decimals = Column(Integer, default=2)
    labels = Column(VARCHAR)
    min = Column(Integer)
    max = Column(Integer)
    height = Column(Integer)

    dashboard = relationship('Dashboard')
    data_source = relationship('DataSource')
    group_by = relationship('ChartGroupBy')

    def as_dict(self):
        group_by_data = {}
        for group in self.group_by:
            group_by_data[group.dashboard_view_id] = group.as_dict()

        return {'id': self.id,
                'dashboard_id': self.dashboard_id,
                'index': self.index,
                'title': self.title,
                'unit': self.unit,
                'color': self.color,
                'type': self.type,
                'query': self.query,
                'data_source_id': self.data_source_id,
                'decimals': self.decimals,
                'labels': self.labels,
                'min': self.min,
                'max': self.max,
                'height': self.height,
                'data_source': self.data_source.as_dict(),
                'group_by': [group.as_dict() for group in self.group_by]}

    def __repr__(self):
        return "Chart<id: %s, title: '%s'>" % (self.id, self.title)
