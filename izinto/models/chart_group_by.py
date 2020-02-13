from sqlalchemy import ForeignKey, Column, Integer, Unicode
from sqlalchemy.orm import relationship

from izinto.models import Base


class ChartGroupBy(Base):
    """ chart group by interval per dashboard view """
    __tablename__ = 'chart_group_by'

    chart_id = Column(Integer, ForeignKey('chart.id', ondelete="cascade"), primary_key=True)
    dashboard_view_id = Column(Integer, ForeignKey('dashboard_view.id', ondelete="cascade"), primary_key=True)
    value = Column(Unicode(length=100))

    dashboard_view = relationship('DashboardView')

    def as_dict(self):

        return {'chart_id': self.chart_id,
                'value': self.value,
                'dashboard_view_id': self.dashboard_view_id,
                'dashboard_view': self.dashboard_view.as_dict()}
