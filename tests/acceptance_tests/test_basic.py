import unittest
from datetime import date, datetime
import decimal

from iso8601.iso8601 import Utc

from kim.serializers import Serializer, Field
from kim.types import (String, Collection, Nested, Integer, Email, Date,
    DateTime, Decimal)
from kim.roles import whitelist


class BasicAcceptanceTests(unittest.TestCase):
    def test_collections_of_nested(self):
        class Inner(Serializer):
            name = Field(String())

        class Outer(Serializer):
            people = Field(Collection(Nested(mapped=Inner)))

        data = {'people': [{'name': 'Jack'}, {'name': 'Mike'}]}

        result = Outer().serialize(data)

        self.assertEquals(result, data)

    def test_collections_of_collections(self):
        class Outer(Serializer):
            rooms = Field(Collection(Collection(Integer())))

        data = {'rooms': [[1, 2, 3], [4, 5, 6]]}

        result = Outer().serialize(data)

        self.assertEquals(result, data)

    def test_collection_transform_serialize(self):
        class Outer(Serializer):
            people = Field(Collection(String(), serialize_member=lambda m: m['name']))

        data = {'people': [{'name': 'Jack'}, {'name': 'Mike'}]}

        result = Outer().serialize(data)

        self.assertEquals(result, {'people': ['Jack', 'Mike']})

    def test_collection_transform_marshal(self):
        class Outer(Serializer):
            people = Field(Collection(String(), marshal_member=lambda m: {'name': m}))

        data = {'people': ['Jack', 'Mike']}
        exp = {'people': [{'name': 'Jack'}, {'name': 'Mike'}]}

        result = Outer().marshal(data)

        self.assertEquals(result, exp)

    def test_self_nesting(self):
        class Inner(Serializer):
            name = Field(String(), source='user_name')

        class Outer(Serializer):
            user = Field(Nested(Inner), source='__self__')

        data = {'user_name': 'jack'}

        result = Outer().serialize(data)

        self.assertEquals(result, {'user': {'name': 'jack'}})

    def test_self_nesting_marshal(self):
        class Inner(Serializer):
            name = Field(String(), source='user_name')

        class Outer(Serializer):
            user = Field(Nested(Inner), source='__self__')
            status = Field(Integer())

        data = {'user': {'name': 'jack'}, 'status': 200}

        result = Outer().marshal(data)

        self.assertEquals(result, {'user_name': 'jack', 'status': 200})

    def test_read_only(self):
        class Outer(Serializer):
            id = Field(String(), read_only=True)
            user = Field(String)

        data = {'user': 'jack', 'id': 'ignore this'}

        result = Outer().marshal(data)

        self.assertEquals(result, {'user': 'jack'})

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

        result = Outer().serialize(data)

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

        marshal_result = Outer().marshal(result)

        self.assertEquals(marshal_result, data)

    def test_many(self):
        class Inner(Serializer):
            name = Field(String(), source='user_name')

        class Outer(Serializer):
            user = Field(Nested(Inner), source='__self__')

        data = [{'user_name': 'jack'}, {'user_name': 'mike'}]

        result = Outer().serialize(data, many=True)

        self.assertEquals(result, [{'user': {'name': 'jack'}},
                                   {'user': {'name': 'mike'}}])

    def test_nested_with_role(self):
        class Inner(Serializer):
            name = Field(String)
            email = Field(String)

        class Outer(Serializer):
            user = Field(Nested(Inner, role=whitelist('name')))

        data = {'user': {'name': 'jack', 'email': 'hello@example.com'}}

        result = Outer().serialize(data)

        self.assertEquals(result, {'user': {'name': 'jack'}})

    def test_nested_when_none(self):
        class Inner(Serializer):
            name = Field(String)
            email = Field(String)

        class Outer(Serializer):
            user = Field(Nested(Inner, role=whitelist('name')), required=False)

        data = {'user': None}

        result = Outer().marshal(data)

        self.assertEquals(result, {'user': None})

    def test_collection_when_none(self):
        class Outer(Serializer):
            mylist = Field(Collection(Integer()), required=False)

        data = {'mylist': None}

        result = Outer().marshal(data)

        self.assertEquals(result, {'mylist': []})
