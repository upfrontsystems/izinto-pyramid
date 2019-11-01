from sqlalchemy import Column, ForeignKey, Integer, VARCHAR
from izinto.models import Base


class UserRole(Base):
    """ association table for users and roles """

    __tablename__ = 'user_role'

    user_id = Column(VARCHAR(length=32), ForeignKey('user.id'), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True, nullable=False)
