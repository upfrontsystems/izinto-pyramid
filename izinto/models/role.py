from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.orm import relationship

from izinto.models.meta import Base
from izinto.models.permission import Permission
from izinto.models.permisson_role import PermissionRole


class Role(Base):
    """ A user's roles """
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=100))

    permissions = relationship(Permission, secondary=PermissionRole.__table__)

    def __repr__(self):
        return '<role(id="%s", name="%s")>' % (self.id, self.name)
