from sqlalchemy import (Column, ForeignKey, Unicode, Integer, VARCHAR)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from izinto.models import Base


class DataSource(Base):
    """
    Data source model Model
    """

    __tablename__ = 'data_source'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode(length=200))
    type = Column(Unicode(length=100))
    url = Column(Unicode(length=200))
    username = Column(Unicode(length=100))
    password = Column(Unicode(length=100))
    database = Column(Unicode(length=200))
    owner_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete="cascade"), nullable=False)

    def as_dict(self):

        return {'id': self.id,
                'name': self.name,
                'type': self.type,
                'url': self.url,
                'username': self.username,
                'password': self.password,
                'database': self.database}

    def __repr__(self):
        return 'DataSource<id: %s, name: %s>' % (self.id, self.name)
