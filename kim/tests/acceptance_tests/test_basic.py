import unittest
from datetime import date, datetime
import decimal

from iso8601.iso8601 import Utc

from kim.serializers import Serializer, Field
from kim.types import (String, Collection, Nested, Integer, Email, Date,
    DateTime, Decimal)


class BasicAcceptanceTests(unittest.TestCase):
    def test_collections_of_nested(self):
        class Inner(Serializer):
            name = Field(String())

        class Outer(Serializer):
            people = Field(Collection(Nested(mapped=Inner)))

        data = {'people': [{'name': 'Jack'}, {'name': 'Mike'}]}

        result = Outer(data).serialize()

        self.assertEquals(result, data)

    def test_collections_of_collections(self):
        class Outer(Serializer):
            rooms = Field(Collection(Collection(Integer())))

        data = {'rooms': [[1, 2, 3], [4, 5, 6]]}

        result = Outer(data).serialize()

        self.assertEquals(result, data)

    def test_self_nesting(self):
        class Inner(Serializer):
            name = Field(String(), source='user_name')

        class Outer(Serializer):
            user = Field(Nested(Inner), source='__self__')

        data = {'user_name': 'jack'}

        result = Outer(data).serialize()

        self.assertEquals(result, {'user': {'name': 'jack'}})

    def test_self_nesting_marshal(self):
        class Inner(Serializer):
            name = Field(String(), source='user_name')

        class Outer(Serializer):
            user = Field(Nested(Inner), source='__self__')
            status = Field(Integer())

        data = {'user': {'name': 'jack'}, 'status': 200}

        result = Outer(input=data).marshal()

        self.assertEquals(result, {'user_name': 'jack', 'status': 200})

    def test_multiple_types(self):
        class Inner(Serializer):
            name = Field(String())
            email = Field(Email())
            alternative_emails = Field(Collection(Email()))
            signup_date = Field(Date(), source='created_at')

        class Outer(Serializer):
            user = Field(Nested(Inner))
            status = Field(Integer())
            updated_at = Field(DateTime())
            cost = Field(Decimal(precision=2))

        data = {'user': {
                        'name': 'Bob',
                        'email': 'bob@bobscaravans.com',
                        'alternative_emails': [
                            'bigbob@gmail.com',
                            'bobscaravansltd@btinternet.com'
                        ],
                        'created_at': date(2014, 4, 8),
                    },
                'status': 200,
                'updated_at': datetime(2014, 4, 8, 6, 12, 43, tzinfo=Utc()),
                'cost': decimal.Decimal("3.50"),
        }

        result = Outer(data).serialize()

        self.assertEquals(result,
            {'user': {
                        'name': 'Bob',
                        'email': 'bob@bobscaravans.com',
                        'alternative_emails': [
                            'bigbob@gmail.com',
                            'bobscaravansltd@btinternet.com'
                        ],
                        'signup_date': '2014-04-08',
                    },
                'status': 200,
                'updated_at': '2014-04-08T06:12:43+00:00',
                'cost': "3.50",
            }
        )

        marshal_result = Outer(input=result).marshal()

        self.assertEquals(marshal_result, data)

    def test_many(self):
        class Inner(Serializer):
            name = Field(String(), source='user_name')

        class Outer(Serializer):
            user = Field(Nested(Inner), source='__self__')

        data = [{'user_name': 'jack'}, {'user_name': 'mike'}]

        result = Outer(data).serialize(many=True)

        self.assertEquals(result, [{'user': {'name': 'jack'}},
                                   {'user': {'name': 'mike'}}])

