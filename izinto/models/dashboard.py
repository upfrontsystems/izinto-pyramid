from sqlalchemy import (Column, Unicode, Integer, ForeignKey, TEXT, VARCHAR, Boolean, LargeBinary)
from sqlalchemy.orm import relationship

from izinto.models import ContainerBase
from izinto.services.user_access import get_user_access


class Dashboard(ContainerBase):
    """
    Dashboard Model inherits from Collection
    """

    __tablename__ = 'dashboard'

    id = Column(ForeignKey('container_base.id', ondelete='CASCADE'), primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.id', ondelete='CASCADE'), nullable=True)
    content = Column(TEXT)
    # a dashboard can be an 'old' or a 'new' type dashboard
    # new type dashboards are html documents stored in `content`
    type = Column(VARCHAR, nullable=False, default='new')
    index = Column(Integer, default=1)
    date_hidden = Column(Boolean)

    collection = relationship('Collection', foreign_keys=[collection_id], backref='dashboards')
    users = relationship('User', secondary="user_dashboard", backref='dashboards')

    __mapper_args__ = {
        'polymorphic_identity': 'dashboard',
    }
    
    def as_dict(self, user_id=None):
        image_data = None
        if self.image:
            image_data = self.image.decode()

        # include user access
        user_access = {}
        if user_id:
            from izinto.models import UserDashboard
            user_access = get_user_access(UserDashboard, 'dashboard_id', self.id, user_id)

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'collection_id': self.collection_id,
                'index': self.index,
                'type': self.type,
                'content': self.content,
                'variables': [var.as_dict() for var in self.variables],
                'date_hidden': self.date_hidden,
                'image': image_data,
                'user_access': user_access}

    def __repr__(self):
        return 'Dashboard<title: %s>' % self.title
