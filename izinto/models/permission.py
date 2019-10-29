from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.orm import relationship

from izinto.models.meta import Base


class Permission(Base):
    """ The permission of a role """
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=100), unique=True)

    roles = relationship('Role', secondary='permission_role')

    def __repr__(self):
        return '<permission(id="%s", name="%s")>' % (self.id, self.name)
