import unittest

from kim.serializers import Serializer, Field
from kim.types import String, Collection, Nested, Integer


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
