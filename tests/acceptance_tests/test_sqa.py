#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from iso8601.iso8601 import Utc

from kim.serializers import Field
from kim.roles import whitelist
from kim import types
from kim.contrib.sqa import SQASerializer, NestedForeignKey, IntegerForeignKey, RelationshipCollection
from kim.exceptions import MappingErrors, ConfigurationError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    signup_date = Column(DateTime, nullable=True)

    contact_details_id = Column(Integer, ForeignKey('contact_detail.id'), nullable=True)
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

        self.user = User(name='foo', contact_details=self.deets,
                         signup_date=datetime(2014, 4, 11, 4, 6, 2))
        self.session.add(self.user)
        self.session.commit()


    def tearDown(self):

        Base.metadata.drop_all(self.engine)

    def test_nested_serialize(self):
        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer), source='contact_details')

        serializer = UserSerializer()
        result = serializer.serialize(self.user)

        exp = {
            'id': self.user.id,
            'full_name': self.user.name,
            'contact': {
                'id': self.deets.id,
                'phone': self.deets.phone,
                'address': {
                    'country': self.address.country,
                    'postcode': self.address.postcode,
                }
            },
            'signup_date': '2014-04-11T04:06:02'
        }
        self.assertDictEqual(result, exp)

    def test_nested_serialize_with_role(self):
        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            email = Field(types.String)

            class Meta:
                roles = {'phone': whitelist('phone')}

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer,
                role=ContactSerializer.Meta.roles['phone']), source='contact_details')

        serializer = UserSerializer()
        result = serializer.serialize(self.user)

        exp = {
            'id': self.user.id,
            'full_name': self.user.name,
            'contact': {
                'phone': self.deets.phone,
            },
            'signup_date': '2014-04-11T04:06:02'
        }
        self.assertDictEqual(result, exp)

    def test_nested_marshal_allow_create(self):
        """When allow_create is True and we pass a nested object without an id,
        we expect a new object to be created and populated with that data."""
        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer, allow_create=True))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer, allow_create=True), source='contact_details')

        data = {
            'full_name': 'bob',
            'contact': {
                'phone': '082345234',
                'address': {
                    'country': 'uk',
                    'postcode': 'sg1 3ab',
                }
            },
            'signup_date': '2014-06-12T19:06:02'
        }

        serializer = UserSerializer()
        result = serializer.marshal(data)

        self.assertTrue(isinstance(result, User))
        self.assertEqual(result.name, 'bob')
        self.assertEqual(result.signup_date, datetime(2014, 6, 12, 19, 6, 2, tzinfo=Utc()))

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

    def test_nested_marshal_allow_create_remote_class(self):
        """When allow_create is True and we pass a nested object without an id,
        we expect a new object to be created and populated with that data.
        When remote_class is also passed, we expect the object to be of that type"""
        class MyRemoteClass(object):
            phone = None

        class MyRemoteSerializer(SQASerializer):
            __model__ = MyRemoteClass

            phone = Field(types.String)
            # address = Field(NestedForeignKey(mapped=AddressSerializer, allow_create=True))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            my_remote_object = Field(NestedForeignKey(mapped=MyRemoteSerializer,
                allow_create=True, remote_class=MyRemoteClass))

        data = {
            'full_name': 'bob',
            'my_remote_object': {
                'phone': '082345234',
            },
        }

        user = User()
        user.my_remote_object = None

        serializer = UserSerializer()
        result = serializer.marshal(data, instance=user)

        remote =result.my_remote_object
        self.assertTrue(isinstance(remote, MyRemoteClass))
        self.assertEqual(remote.phone, '082345234')

    def test_nested_marshal_allow_updates_in_place(self):
        """When allow_updates_in_place is True and we pass a nested object without an id,
        and there is already an object associated with this foreign key,
        we expect the existing object to be updated with that data."""
        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)

        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer(), read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer, allow_updates_in_place=True))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer(), read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime(), required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer, allow_updates_in_place=True), source='contact_details')

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

        serializer = UserSerializer()
        result = serializer.marshal(data, instance=self.user)

        self.assertTrue(isinstance(result, User))
        self.assertEqual(result.name, 'bob')

        contact_details = result.contact_details
        self.assertTrue(isinstance(contact_details, ContactDetail))
        self.assertEqual(contact_details.phone, '082345234')
        self.assertEqual(contact_details.email, 'mike@mike.com')

        address = result.contact_details.address
        self.assertTrue(isinstance(address, Address))
        self.assertEqual(address.country, 'uk')
        self.assertEqual(address.postcode, 'sg1 3ab')
        self.assertEqual(address.city, 'london')

        self.session.add(result)
        self.session.commit()

    def test_foreignkey_field_pass_id(self):
        """With default options, when a nested object is passed with an id,
        we expect that id to be resolved and the foreign key set to the
        resolved object"""
        def contact_getter(id):
            return self.session.query(ContactDetail).get(id)

        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)

        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer,
                getter=contact_getter), source='contact_details')

        data = {
            'full_name': 'bob',
            'contact': {'id': self.deets.id},
        }

        serializer = UserSerializer()
        result = serializer.marshal(data)

        self.assertTrue(isinstance(result, User))
        self.assertEqual(result.name, 'bob')

        contact_details = result.contact_details
        self.assertTrue(isinstance(contact_details, ContactDetail))
        self.assertEqual(contact_details.id, self.deets.id)

        address = result.contact_details.address
        self.assertTrue(isinstance(address, Address))
        self.assertEqual(address.id, self.address.id)

        self.session.add(result)
        self.session.commit()

        serializer = UserSerializer()
        serialized = serializer.serialize(result)

        exp = {
            'id': result.id,
            'full_name': 'bob',
            'contact': {
                'id': self.deets.id,
                'phone': self.deets.phone,
                'address': {
                    'country': self.address.country,
                    'postcode': self.address.postcode,
                }
            },
            'signup_date': None,
        }
        self.assertDictEqual(serialized, exp)

    def test_foreignkey_field_getter_error(self):
        """When we pass an id to a foreign key, and the getter for the type
        returns False, we expect an error to be raised."""
        def contact_getter(id):
            return False

        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)

        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer,
                getter=contact_getter), source='contact_details')

        data = {
            'full_name': 'bob',
            'contact': {'id': self.deets.id},
        }

        serializer = UserSerializer()

        with self.assertRaises(MappingErrors):
            serializer.marshal(data)

    def test_foreignkey_field_not_required(self):
        """When a foreign key field is not required, we expect it to be ignored
        if not present in the marshalled data."""
        def contact_getter(id):
            return False

        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer,
                getter=contact_getter),
                required=False, source='contact_details')

        data = {
            'full_name': 'bob',
        }

        serializer = UserSerializer()

        result = serializer.marshal(data)

        self.assertIsNone(result.contact_details)

    def test_nested_marshal_allow_updates_false(self):
        """With the default settings (allow_updates=False), if a nested object
        is passed without an id, we expect an error to be raised."""
        def contact_getter(id):
            return self.session.query(ContactDetail).get(id)

        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)

        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer,
                getter=contact_getter), source='contact_details')

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

        serializer = UserSerializer()
        with self.assertRaises(MappingErrors):
            serializer.marshal(data)

    def test_nested_marshal_allow_updates(self):
        """When allow_updates is True, if a nested object is passed with an id,
        we expect the object with that id to be resolved and updated with that
        data."""
        def contact_getter(id):
            return self.session.query(ContactDetail).get(id)

        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)

        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer, allow_create=True))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer,
                getter=contact_getter, allow_updates=True), source='contact_details')

        data = {
            'full_name': 'bob',
            'contact': {
                'id': self.deets.id,
                'phone': '082345234',
                'address': {
                    'country': 'uk',
                    'postcode': 'sg1 3ab',
                }
            }
        }

        serializer = UserSerializer()
        result = serializer.marshal(data)

        self.session.flush()
        self.session.expire_all()

        self.assertEqual(self.deets.phone, '082345234')
        self.assertNotEqual(self.deets.address.id, self.address.id)

    def test_nested_serialize_collection(self):
        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)

        # Contrary to other tests, this time we go via the backref contact -> users
        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)

            users = Field(RelationshipCollection(NestedForeignKey(mapped=UserSerializer)))

        contact = ContactDetail(phone='235345', address=self.address)

        user1 = User(name='bob', contact_details=contact)
        user2 = User(name='jim', contact_details=contact)
        user3 = User(name='harry', contact_details=contact)

        self.session.add_all([contact, user1, user2, user3])
        self.session.flush()

        serializer = ContactSerializer()
        result = serializer.serialize(contact)

        self.assertEqual(result,
            {
                'id': contact.id,
                'phone': '235345',
                'users': [
                    {'id': user1.id, 'signup_date': None, 'full_name': 'bob'},
                    {'id': user2.id, 'signup_date': None, 'full_name': 'jim'},
                    {'id': user3.id, 'signup_date': None, 'full_name': 'harry'},
                ]
            })

    def test_nested_marshal_collection_id_only(self):
        """When allow_updates is True, if a nested object is passed with an id,
        we expect the object with that id to be resolved and updated with that
        data."""
        def user_getter(id):
            return self.session.query(User).get(id)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)

        # Contrary to other tests, this time we go via the backref contact -> users
        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)

            users = Field(RelationshipCollection(NestedForeignKey(mapped=UserSerializer,
                getter=user_getter)))

        user1 = User(name='bob')
        user2 = User(name='jim')
        user3 = User(name='harry')

        self.session.add_all([user1, user2, user3])
        self.session.flush()

        data = {
            'phone': '0124234',
            'users': [
                {'id': user1.id},
                {'id': user2.id},
                {'id': user3.id},
            ]
        }

        serializer = ContactSerializer()
        result = serializer.marshal(data)

        self.assertEqual(user1.contact_details_id, result.id)
        self.assertEqual(user2.contact_details_id, result.id)
        self.assertEqual(user3.contact_details_id, result.id)

    def test_nested_marshal_collection_allow_update(self):
        """When allow_updates is True, if a nested object is passed with an id,
        we expect the object with that id to be resolved and updated with that
        data."""
        def user_getter(id):
            return self.session.query(User).get(id)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)

        # Contrary to other tests, this time we go via the backref contact -> users
        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)

            users = Field(RelationshipCollection(NestedForeignKey(mapped=UserSerializer,
                getter=user_getter, allow_updates=True)))

        user1 = User(name='bob')
        user2 = User(name='jim')
        user3 = User(name='harry')

        self.session.add_all([user1, user2, user3])
        self.session.flush()

        data = {
            'phone': '0124234',
            'users': [
                {'id': user1.id, 'full_name': 'this is a new name'},
                {'id': user2.id, 'full_name': 'this is another name'},
                {'id': user3.id, 'full_name': 'this is a third name'},
            ]
        }

        serializer = ContactSerializer()
        result = serializer.marshal(data)

        self.assertEqual(user1.contact_details_id, result.id)
        self.assertEqual(user2.contact_details_id, result.id)
        self.assertEqual(user3.contact_details_id, result.id)
        self.assertEqual(user1.name, 'this is a new name')
        self.assertEqual(user2.name, 'this is another name')
        self.assertEqual(user3.name, 'this is a third name')

    def test_nested_marshal_collection_allow_updates_in_place(self):
        """When allow_updates is True, if a nested object is passed with an id,
        we expect the object with that id to be resolved and updated with that
        data."""
        def user_getter(id):
            return self.session.query(User).get(id)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)

        # Contrary to other tests, this time we go via the backref contact -> users
        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)

            users = Field(RelationshipCollection(NestedForeignKey(mapped=UserSerializer,
                getter=user_getter, allow_updates_in_place=True)))

        contact = ContactDetail(phone='235345', address=self.address)

        user1 = User(name='bob', contact_details=contact)
        user2 = User(name='jim', contact_details=contact)
        user3 = User(name='harry', contact_details=contact)

        self.session.add_all([contact, user1, user2, user3])
        self.session.flush()

        data = {
            'phone': '0124234',
            'users': [
                {'full_name': 'this is a new name'},
                {'full_name': 'this is another name'},
                {'full_name': 'this is a third name'},
            ]
        }

        serializer = ContactSerializer()
        result = serializer.marshal(data, instance=contact)

        self.assertEqual(user1.contact_details_id, result.id)
        self.assertEqual(user2.contact_details_id, result.id)
        self.assertEqual(user3.contact_details_id, result.id)
        self.assertEqual(user1.name, 'this is a new name')
        self.assertEqual(user2.name, 'this is another name')
        self.assertEqual(user3.name, 'this is a third name')

    def test_nested_marshal_collection_allow_create(self):
        """When allow_updates is True, if a nested object is passed with an id,
        we expect the object with that id to be resolved and updated with that
        data."""
        def user_getter(id):
            return self.session.query(User).get(id)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)

        # Contrary to other tests, this time we go via the backref contact -> users
        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)

            users = Field(RelationshipCollection(NestedForeignKey(mapped=UserSerializer,
                getter=user_getter, allow_create=True)))

        contact = ContactDetail(phone='235345', address=self.address)

        self.session.add(contact)
        self.session.flush()

        data = {
            'phone': '0124234',
            'users': [
                {'full_name': 'this is a new name'},
                {'full_name': 'this is another name'},
                {'full_name': 'this is a third name'},
            ]
        }

        serializer = ContactSerializer()
        result = serializer.marshal(data, instance=contact)

        self.session.add(result)
        self.session.flush()

        self.assertEqual(result.users[0].contact_details_id, result.id)
        self.assertEqual(result.users[1].contact_details_id, result.id)
        self.assertEqual(result.users[2].contact_details_id, result.id)
        self.assertEqual(result.users[0].name, 'this is a new name')
        self.assertEqual(result.users[1].name, 'this is another name')
        self.assertEqual(result.users[2].name, 'this is a third name')


    def test_foreignkey_field_allow_create_allow_updates_in_place_mutually_exclusive(self):
        with self.assertRaises(ConfigurationError):
            class ContactSerializer(SQASerializer):
                __model__ = ContactDetail

                id = Field(types.Integer, read_only=True)
                phone = Field(types.String)

            class UserSerializer(SQASerializer):
                __model__ = User

                id = Field(types.Integer, read_only=True)
                contact = Field(NestedForeignKey(mapped=ContactSerializer,
                    allow_updates_in_place=True, allow_create=True), source='contact_details')


    def test_serialize_dot_notation(self):
        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            phone = Field(types.String, source='contact_details.phone')

        serializer = UserSerializer()
        result = serializer.serialize(self.user)

        exp = {
            'id': self.user.id,
            'full_name': self.user.name,
            'phone': self.deets.phone,
        }
        self.assertDictEqual(result, exp)

    def test_roles(self):
        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime)

            class Meta:
                roles = {'name_only': whitelist('full_name')}

        serializer = UserSerializer()
        result = serializer.serialize(self.user, role='name_only')

        exp = {
            'full_name': self.user.name,
        }
        self.assertDictEqual(result, exp)

    def test_marshal_dot_notation(self):
        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer(), read_only=True)
            full_name = Field(types.String, source='name')
            phone = Field(types.String, source='contact_details.phone')

        serializer = UserSerializer()

        data = {
            'full_name': 'fred',
            'phone': '234765464',
        }

        result = serializer.marshal(data, instance=self.user)

        self.assertEqual(result.name, 'fred')
        self.assertEqual(result.contact_details.phone, '234765464')

        self.session.add(result)
        self.session.commit()

    def test_integerforeignkey_field(self):
        def contact_getter(id):
            return self.session.query(ContactDetail).get(id)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(IntegerForeignKey(getter=contact_getter), source='contact_details_id')

        data = {
            'full_name': 'bob',
            'contact': self.deets.id,
        }

        serializer = UserSerializer()
        result = serializer.marshal(data)

        self.session.add(result)
        self.session.commit()

        self.assertTrue(isinstance(result, User))
        self.assertEqual(result.name, 'bob')

        contact_details = result.contact_details
        self.assertTrue(isinstance(contact_details, ContactDetail))
        self.assertEqual(contact_details.id, self.deets.id)


        self.session.add(self.deets)

        serializer = UserSerializer()
        serialized = serializer.serialize(result)

        exp = {
            'id': result.id,
            'full_name': 'bob',
            'contact': self.deets.id,
            'signup_date': None,
        }
        self.assertDictEqual(serialized, exp)

    def test_integerforeignkey_field_as_string(self):
        def contact_getter(id):
            return self.session.query(ContactDetail).get(id)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(IntegerForeignKey(getter=contact_getter), source='contact_details_id')

        data = {
            'full_name': 'bob',
            'contact': str(self.deets.id),
        }

        serializer = UserSerializer()
        result = serializer.marshal(data)

        self.session.add(result)
        self.session.commit()

        self.assertTrue(isinstance(result, User))
        self.assertEqual(result.name, 'bob')

        contact_details = result.contact_details
        self.assertTrue(isinstance(contact_details, ContactDetail))
        self.assertEqual(contact_details.id, self.deets.id)


        self.session.add(self.deets)

        serializer = UserSerializer()
        serialized = serializer.serialize(result)

        exp = {
            'id': result.id,
            'full_name': 'bob',
            'contact': self.deets.id,
            'signup_date': None,
        }
        self.assertDictEqual(serialized, exp)

    def test_integerforeignkey_field_invalid(self):
        def contact_getter(id):
            return False

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer(), read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime(), required=False)
            contact = Field(IntegerForeignKey(getter=contact_getter), source='contact_details_id')

        data = {
            'full_name': 'bob',
            'contact': self.deets.id,
        }

        serializer = UserSerializer()

        with self.assertRaises(MappingErrors):
            serializer.marshal(data)

    def test_integerforeignkey_field_invalid_raises(self):
        def contact_getter(id):
            raise NoResultFound()

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(IntegerForeignKey(getter=contact_getter), source='contact_details_id')

        data = {
            'full_name': 'bob',
            'contact': self.deets.id,
        }

        serializer = UserSerializer()

        with self.assertRaises(MappingErrors):
            serializer.marshal(data)


    def test_nested_serialize_raw(self):
        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer))

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer), source='contact_details')

        serializer = UserSerializer()

        result = self.session.query(
            User.id,
            User.name,
            User.signup_date,
            ContactDetail.id.label('contact_details__id'),
            ContactDetail.phone.label('contact_details__phone'),
            Address.country.label('contact_details__address__country'),
            Address.postcode.label('contact_details__address__postcode'),
        ).join(ContactDetail, Address).one()

        result = serializer.serialize(result, raw=True)

        exp = {
            'id': self.user.id,
            'full_name': self.user.name,
            'contact': {
                'id': self.deets.id,
                'phone': self.deets.phone,
                'address': {
                    'country': self.address.country,
                    'postcode': self.address.postcode,
                }
            },
            'signup_date': '2014-04-11T04:06:02'
        }
        self.assertDictEqual(result, exp)

    def test_nested_serialize_raw_all_none(self):
        class AddressSerializer(SQASerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(SQASerializer):
            __model__ = ContactDetail

            id = Field(types.Integer, read_only=True)
            phone = Field(types.String)
            address = Field(NestedForeignKey(mapped=AddressSerializer), required=False)

        class UserSerializer(SQASerializer):
            __model__ = User

            id = Field(types.Integer, read_only=True)
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime, required=False)
            contact = Field(NestedForeignKey(mapped=ContactSerializer), source='contact_details')

        serializer = UserSerializer()

        user = User(name='foo', signup_date=datetime(2014, 4, 11, 4, 6, 2))

        self.session.add(user)
        self.session.commit()

        result = self.session.query(
            User.id,
            User.name,
            User.signup_date,
            ContactDetail.id.label('contact_details__id'),
            ContactDetail.phone.label('contact_details__phone'),
            Address.country.label('contact_details__address__country'),
            Address.postcode.label('contact_details__address__postcode'),
        ).outerjoin(ContactDetail, Address).filter(User.id == user.id).one()

        result = serializer.serialize(result, raw=True)

        exp = {
            'id': user.id,
            'full_name': user.name,
            'contact': None,
            'signup_date': '2014-04-11T04:06:02'
        }
        self.assertDictEqual(result, exp)