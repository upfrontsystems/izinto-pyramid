from izinto.models import Base
from sqlalchemy import (Column, Unicode, Integer, LargeBinary)
from sqlalchemy.orm import relationship


class ContainerBase(Base):
    """
    Base class of containers and dashboards
    """

    __tablename__ = 'container_base'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Unicode(length=100))
    description = Column(Unicode(length=500))
    image = Column(LargeBinary)
    polymorphic_type = Column(Unicode(length=50))

    variables = relationship('Variable', backref="container")

    __mapper_args__ = {
        'polymorphic_identity': 'container_base',
        'polymorphic_on': polymorphic_type
    }

    def as_dict(self, user_id=None):
        image_data = None
        if self.image:
            image_data = self.image.decode()

        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'image': image_data}

    def __repr__(self):
        return 'ContainerBase<id: %s, title: "%s">' % (self.id, self.title)
