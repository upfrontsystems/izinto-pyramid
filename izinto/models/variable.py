from sqlalchemy import (Column, ForeignKey, Unicode, Integer, UniqueConstraint)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Variable(Base):
    """
    Variable Model
    """

    __tablename__ = 'variable'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode(length=100))
    value = Column(Unicode(length=100))
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete='CASCADE'), nullable=False)

    dashboard = relationship('Dashboard')

    __table_args__ = (UniqueConstraint('value', 'dashboard_id'),)

    def as_dict(self):

        return {'id': self.id,
                'name': self.name,
                'value': self.value,
                'dashboard_id': self.dashboard_id}

    def __repr__(self):
        return 'Variable<name: %s>' % self.name
