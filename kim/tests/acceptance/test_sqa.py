#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.serializers import Serializer, Field
from kim.roles import Role
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
    address_id = Column(Integer, ForeignKey('address.id'), nullable=False)

    address = relationship("Address", backref="contact")
    user = relationship("User", backref="contact_details")


class Address(Base):

    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    address_1 = Column(String, nullable=False)
    address_2 = Column(String, nullable=False)
    postcode = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)


class AddressSerializer(Serializer):

    country = Field(types.String)
    postcode = Field(types.String)


class ContactSerializer(Serializer):

    id = Field(types.Integer)
    phone = Field(types.String)
    address = Field(types.Nested(mapped=AddressSerializer,
                                 role=Role('foo', 'country', 'postcode')))


class UserSerializer(Serializer):

    id = Field(types.Integer)
    full_name = Field(types.String, source='name')
    contacts = Field(
                    types.Collection(types.Nested(mapped=ContactSerializer,
                                       role=Role('public',
                                                 'phone',
                                                 'address'))),
                    source='contact_details'
                )

class SQAAcceptanceTests(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        self.user = User(name='foo')
        self.session.add(self.user)
        self.session.flush()

        self.address = Address(address_1='2 easy street',
                               address_2='other',
                               postcode='sm00ln',
                               city='london',
                               country='UK')
        self.session.add(self.user)
        self.session.flush()

        self.deets = ContactDetail(user=self.user,
                                   address=self.address,
                                   phone='07967168590',
                                   email='mike@mike.com')

        self.session.add(self.deets)
        self.session.commit()

    def tearDown(self):

        Base.metadata.drop_all(self.engine)

    def test_nested_nested_role_base_serialize(self):

        serializer = UserSerializer(data=self.user)
        result = serializer.serialize()

        exp = {
            'id': self.user.id,
            'full_name': self.user.name,
            'contacts': [{
                'phone': self.deets.phone,
                'address': {
                    'country': self.address.country,
                    'postcode': self.address.postcode,
                }
            }]
        }
        self.assertDictEqual(result, exp)
