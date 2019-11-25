from sqlalchemy import ForeignKey, Column, Integer, VARCHAR
from izinto.models import Base


class UserCollection(Base):
    """ association table for users and collections """
    __tablename__ = 'user_collection'

    user_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete="cascade"), primary_key=True, nullable=False)
    collection_id = Column(Integer, ForeignKey('collection.id', ondelete="cascade"), primary_key=True, nullable=False)
