from izinto.models import Base
from sqlalchemy import (Column, Unicode, Integer, LargeBinary)
from sqlalchemy.orm import relationship

from izinto.services.user_access import get_user_access


class Collection(Base):
    """
    A collection of dashboards
    """

    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Unicode(length=100))
    description = Column(Unicode(length=500))
    image = Column(LargeBinary)

    users = relationship('User', secondary="user_collection", backref="collections")
    dashboards = relationship('Dashboard')

    def as_dict(self, user_id=None):
        image_data = None
        if self.image:
            image_data = self.image.decode()

        # include user access
        user_access = {}
        if user_id:
            from izinto.models import UserCollection
            user_access = get_user_access(UserCollection, 'collection_id', self.id, user_id)

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'image': image_data,
                'user_access': user_access}

    def __repr__(self):
        return 'Collection<id: %s, title: "%s">' % (self.id, self.title)
