from sqlalchemy import (Column, Unicode, Integer, ForeignKey, TEXT, UniqueConstraint)
from sqlalchemy.orm import relationship

from izinto.models import Base


class Branding(Base):
    """
    App branding Model
    """

    __tablename__ = 'branding'

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(Unicode(length=500))
    favicon = Column(Unicode(length=500))
    logo = Column(Unicode(length=500))
    banner = Column(Unicode(length=500))
    
    def as_dict(self):
        return {'id': self.id,
                'hostname': self.hostname,
                'favicon': self.favicon,
                'logo': self.logo,
                'banner': self.banner}

    def __repr__(self):
        return 'Branding<id: %s>' % self.id
