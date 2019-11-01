import logging
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import VARCHAR

from izinto.models import Base

log = logging.getLogger(__name__)


class OTP(Base):
    """One Time Pins (OTP's) are how emails and cellphone numbers are be validated."""

    __tablename__ = 'otp_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(Text)
    otp = Column(Text)
    secret = Column(Text)  # uuid.uuid4
    timestamp = Column(DateTime)
    user_id = Column(VARCHAR(length=32), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    @classmethod
    def clean_identifier(cls, identifier):
        return identifier.strip().replace(' ', '')
