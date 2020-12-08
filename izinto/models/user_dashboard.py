from sqlalchemy.orm import relationship

from izinto.models import Base
from sqlalchemy import ForeignKey, Column, Integer, VARCHAR


class UserDashboard(Base):
    """ association table for users and dashboard """
    __tablename__ = 'user_dashboard'

    user_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete="cascade"), primary_key=True, nullable=False)
    dashboard_id = Column(Integer, ForeignKey('dashboard.id', ondelete="cascade"), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)

    role = relationship('Role')
    user = relationship('User')

    def as_dict(self):
        """
        Return object as json dictionary
        :return:
        """
        role = self.role and self.role.name

        return {'user_id': self.user_id,
                'user': self.user.as_dict(),
                'dashboard_id': self.dashboard_id,
                'role_id': self.role_id,
                'role': role}
