from sqlalchemy import ForeignKey, Column, Integer

from izinto.models.meta import Base


class PermissionRole(Base):
    """ association table for permissions and roles """
    __tablename__ = 'permission_role'

    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True, nullable=False)
    permission_id = Column(Integer, ForeignKey('permission.id'), primary_key=True, nullable=False)
