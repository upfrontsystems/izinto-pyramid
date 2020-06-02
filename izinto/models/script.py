from sqlalchemy import Column, ForeignKey, TEXT, Unicode, Integer
from sqlalchemy.orm import relationship

from izinto.models import Base


class Script(Base):
    """
    Javascript to render visualisations on a dashboard, typically using D3.js or ObservableHQ notebooks.
    """

    __tablename__ = 'script'

    id = Column(Integer, primary_key=True, index=True)
    index = Column(Integer)
    title = Column(Unicode(length=100), nullable=False)
    content = Column(TEXT)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete='CASCADE'))

    dashboard = relationship('Dashboard')

    def as_dict(self):
        return {
            'id': self.id,
            'dashboard_id': self.dashboard_id,
            'index': self.index,
            'title': self.title,
            'content': self.content
        }

    def __repr__(self):
        return "Script<id: %s, title: '%s'>" % (self.id, self.title)
