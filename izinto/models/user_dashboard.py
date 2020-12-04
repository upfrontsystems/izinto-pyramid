from sqlalchemy import ForeignKey, Column, Integer, VARCHAR
from izinto.models import Base


class UserDashboard(Base):
    """ association table for users and dashboard """
    __tablename__ = 'user_dashboard'

    user_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete="cascade"), primary_key=True, nullable=False)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete="cascade"), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
