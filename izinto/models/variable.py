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
    container_id = Column(Integer, ForeignKey('container_base.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (UniqueConstraint('name', 'container_id'),)

    def as_dict(self):

        return {'id': self.id,
                'name': self.name,
                'value': self.value,
                'container_id': self.container_id}

    def __repr__(self):
        return 'Variable<name: %s>' % self.name
