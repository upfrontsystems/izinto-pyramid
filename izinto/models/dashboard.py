from sqlalchemy import (Column, ForeignKey, VARCHAR, Unicode, Integer)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Dashboard(Base):
    """
    Dashboard Model
    """

    __tablename__ = 'dashboard'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Unicode(length=100))
    description = Column(Unicode(length=500))
    user_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete='CASCADE'))

    user = relationship('User')
    variables = relationship('Variable')

    def as_dict(self):

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'user_id': self.user_id,
                'variables': [var.as_dict() for var in self.variables]}

    def __repr__(self):
        return 'Dashboard<title: %s>' % self.title
