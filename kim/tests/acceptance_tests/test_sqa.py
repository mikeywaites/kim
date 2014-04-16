#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.serializers import Serializer, Field
from kim.roles import Role
from kim import types
from kim.contrib.sqa import SQASerializer

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
    contact = Column(Integer, ForeignKey('contact_detail.id'), nullable=False)
    contact_details = relationship("ContactDetail", backref="users")


class ContactDetail(Base):

    __tablename__ = "contact_detail"

    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address_id = Column(Integer, ForeignKey('address.id'), nullable=False)

    address = relationship("Address", backref="contact")


class Address(Base):

    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    address_1 = Column(String, nullable=True)
    address_2 = Column(String, nullable=True)
    postcode = Column(String, nullable=False)
    city = Column(String, nullable=True)
    country = Column(String, nullable=False)


class AddressSerializer(SQASerializer):
    __model__ = Address

    country = Field(types.String)
    postcode = Field(types.String)


class ContactSerializer(SQASerializer):
    __model__ = ContactDetail

    id = Field(types.Integer(read_only=True))
    phone = Field(types.String)
    address = Field(types.Nested(mapped=AddressSerializer,
                                 role=Role('foo', 'country', 'postcode')))


class UserSerializer(SQASerializer):
    __model__ = User

    id = Field(types.Integer(read_only=True))
    full_name = Field(types.String, source='name')
    contact = Field(types.Nested(mapped=ContactSerializer), source='contact_details')
    # contacts = Field(
    #                 types.Collection(types.Nested(mapped=ContactSerializer,
    #                                    role=Role('public',
    #                                              'phone',
    #                                              'address'))),
    #                 source='contact_details'
    #             )

class SQAAcceptanceTests(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

        self.address = Address(address_1='2 easy street',
                               address_2='other',
                               postcode='sm00ln',
                               city='london',
                               country='UK')
        self.deets = ContactDetail(address=self.address,
                           phone='07967168590',
                           email='mike@mike.com')


        self.session.add(self.address)
        self.session.flush()

        self.session.add(self.deets)
        self.session.flush()

        self.user = User(name='foo', contact_details=self.deets)
        self.session.add(self.user)
        self.session.commit()


    def tearDown(self):

        Base.metadata.drop_all(self.engine)

    # def test_nested_nested_role_base_serialize(self):

    #     serializer = UserSerializer(instance=self.user)
    #     result = serializer.serialize()

    #     exp = {
    #         'id': self.user.id,
    #         'full_name': self.user.name,
    #         'contacts': [{
    #             'phone': self.deets.phone,
    #             'address': {
    #                 'country': self.address.country,
    #                 'postcode': self.address.postcode,
    #             }
    #         }]
    #     }
    #     self.assertDictEqual(result, exp)

    def test_nested_nested_role_base_marshal(self):

        data = {
            'full_name': 'bob',
            'contact': {
                'phone': '082345234',
                'address': {
                    'country': 'uk',
                    'postcode': 'sg1 3ab',
                }
            }
        }

        serializer = UserSerializer(input=data)
        result = serializer.marshal()

        self.assertTrue(isinstance(result, User))
        self.assertEqual(result.name, 'bob')

        contact_details = result.contact_details
        self.assertTrue(isinstance(contact_details, ContactDetail))
        self.assertEqual(contact_details.phone, '082345234')

        address = result.contact_details.address
        self.assertTrue(isinstance(address, Address))
        self.assertEqual(address.country, 'uk')
        self.assertEqual(address.postcode, 'sg1 3ab')

        self.assertIsNone(result.id)

        self.session.add(result)
        self.session.commit()

        self.assertIsNotNone(result.id)
