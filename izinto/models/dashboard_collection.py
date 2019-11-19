from sqlalchemy import ForeignKey, Column, Integer, VARCHAR
from izinto.models import Base


class DashboardCollection(Base):
    """ association table for dashboards and collections """
    __tablename__ = 'dashboard_collection'

    dashboard_id = Column(Integer, ForeignKey('dashboard.id'), primary_key=True, nullable=False)
    collection_id = Column(Integer, ForeignKey('collection.id'), primary_key=True, nullable=False)
    order = Column(Integer, autoincrement=True)
