#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.serializers import Serializer, Field
from kim import types

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)



class ContactDetail(Base):

    __tablename__ = "contact_detail"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address_1 = Column(String, nullable=False)
    address_2 = Column(String, nullable=False)
    postcode = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)

    user = relationship("User", backref="contact_details")


class AddressSerializer(Serializer):

    phone = Field(String)


class UserSerializer(Serializer):

    id = Field(types.Integer)
    full_name = Field(types.String, source='name')
    addresses = Field(types.Nested(mapped=AddressSerializer),
                      source='contact_details')


class SQAAcceptanceTests(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        self.user = User(name='foo')
        self.session.add(self.user)
        self.session.flush()

        deets = ContactDetail(user=self.user,
                              phone='07967168590',
                              email='mike@mike.com',
                              address_1='2 easy street',
                              address_2='other',
                              postcode='sm00ln',
                              city='london',
                              country='UK')

        self.session.add(deets)
        self.session.commit()

    def tearDown(self):

        Base.metadata.drop_all(self.engine)

    def test_foo(self):

        serializer = UserSerializer(data=self.user)
        serializer.serialize()
        import ipdb; ipdb.set_trace()
        print 'foo'
