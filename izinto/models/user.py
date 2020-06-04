import codecs
import hashlib
import os
import uuid
from sqlalchemy import (Column, Unicode, Boolean, func, VARCHAR)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from izinto.models import Base


def new_uuid():
    """ Return a new uuid id """
    return uuid.uuid4().hex


class User(Base):
    """
    User Model
    """

    __tablename__ = 'user'

    id = Column(VARCHAR, primary_key=True, index=True, default=new_uuid)
    firstname = Column(Unicode(length=100), nullable=False)
    surname = Column(Unicode(length=100), nullable=False)
    telephone = Column(Unicode(100), index=True, nullable=True)
    address = Column(VARCHAR, nullable=True)
    password = Column(Unicode(length=100), nullable=True)
    salt = Column(Unicode(length=100), nullable=True)
    email = Column(Unicode(255), index=True, unique=True, nullable=True)
    confirmed_registration = Column(Boolean, nullable=False, default=False)
    inactive = Column(Boolean, default=False)

    otp = relationship('OTP', uselist=False)
    roles = relationship('Role', secondary="user_role")

    @hybrid_property
    def fullname(self):
        name = '%s %s' % (self.firstname,  self.surname)
        return name.strip()

    @fullname.expression
    def fullname(cls):
        space = ''
        if cls.firstname and cls.surname:
            space = ' '
        return cls.firstname + space + cls.surname

    def as_dict(self):

        role = self.roles[0].name

        return {'id': self.id,
                'firstname': self.firstname,
                'surname': self.surname,
                'fullname': self.fullname,
                'email': self.email,
                'telephone': self.telephone,
                'role': role,
                'roles': [rol.name for rol in self.roles],
                'address': self.address,
                'inactive': self.inactive}

    def validate_password(self, password):
        """ validate password """
        return hashlib.sha256((self.salt + password).
                              encode('utf-8')).hexdigest() == self.password

    def set_password(self, password):
        """ set password """
        salt = codecs.encode(os.urandom(32), 'hex').decode()
        h = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        h = str(h)
        self.salt = salt
        self.password = h

    def __repr__(self):
        return 'User<id: %s, firstname: %s, surname: %s>' % (self.id, self.firstname, self.surname)

    def has_role(self, rolename):
        for role in self.roles:
            if role.name == rolename:
                return True
        return False
