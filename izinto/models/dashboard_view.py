from sqlalchemy import (Column, Unicode, Integer)
from izinto.models import Base


class DashboardView(Base):
    """
    View option for dashboard page
    """

    __tablename__ = 'dashboard_view'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode(length=200))
    icon = Column(Unicode(length=100))

    def as_dict(self):

        return {'id': self.id,
                'name': self.name,
                'icon': self.icon}

    def __repr__(self):
        return 'DashboardView<id: %s, name: %s>' % (self.id, self.name)
