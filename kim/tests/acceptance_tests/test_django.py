import unittest
from datetime import datetime
from iso8601.iso8601 import Utc


# Begin Django set up bollocks
from django.conf import settings

settings.configure(
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    INSTALLED_APPS=('kim.tests.acceptance_tests.django_test_harness',),
    USE_TZ=True)

from .django_test_harness.models import User, ContactDetail, Address

from django.core.management import call_command
call_command('syncdb')
# End Django set up bollocks


from kim.serializers import Field
from kim import types
from kim.contrib.django_adapter import DjangoSerializer


class DjangoAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.address = Address(address_1='2 easy street',
                               address_2='other',
                               postcode='sm00ln',
                               city='london',
                               country='UK')
        self.address.save()

        self.deets = ContactDetail(address=self.address,
                           phone='07967168590',
                           email='mike@mike.com')

        self.deets.save()

        self.user = User(name='foo', contact_details=self.deets,
                         signup_date=datetime(2014, 4, 11, 4, 6, 2))

        self.user.save()

    def test_nested_serialize(self):
        class AddressSerializer(DjangoSerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(DjangoSerializer):
            __model__ = ContactDetail

            id = Field(types.Integer(read_only=True))
            phone = Field(types.String)
            address = Field(types.Nested(mapped=AddressSerializer))

        class UserSerializer(DjangoSerializer):
            __model__ = User

            id = Field(types.Integer(read_only=True))
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime(required=False))
            contact = Field(types.Nested(mapped=ContactSerializer), source='contact_details')

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

    def test_nested_marshal_existing_object(self):
        class AddressSerializer(DjangoSerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(DjangoSerializer):
            __model__ = ContactDetail

            id = Field(types.Integer(read_only=True))
            phone = Field(types.String)
            address = Field(types.Nested(mapped=AddressSerializer))

        class UserSerializer(DjangoSerializer):
            __model__ = User

            id = Field(types.Integer(read_only=True))
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime(required=False))
            contact = Field(types.Nested(mapped=ContactSerializer,
                marshal_by_key_only=False), source='contact_details')

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

        result.save()

    def test_nested_marshal_new_object(self):
        class AddressSerializer(DjangoSerializer):
            __model__ = Address

            country = Field(types.String)
            postcode = Field(types.String)


        class ContactSerializer(DjangoSerializer):
            __model__ = ContactDetail

            id = Field(types.Integer(read_only=True))
            phone = Field(types.String)
            address = Field(types.Nested(mapped=AddressSerializer))

        class UserSerializer(DjangoSerializer):
            __model__ = User

            id = Field(types.Integer(read_only=True))
            full_name = Field(types.String, source='name')
            signup_date = Field(types.DateTime(required=False))
            contact = Field(types.Nested(mapped=ContactSerializer,
                marshal_by_key_only=False), source='contact_details')

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

        result.save()

        self.assertIsNotNone(result.id)
