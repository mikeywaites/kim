import unittest

from kim.serializers import Serializer, Field
from kim import types


class BasicAcceptanceTests(unittest.TestCase):
    def test_collections_of_nested(self):
        class Inner(Serializer):
            name = Field(types.String())

        class Outer(Serializer):
            people = Field(types.Collection(types.Nested(mapped=Inner)))

        data = {'people': [{'name': 'Jack'}, {'name': 'Mike'}]}

        result = Outer(data).serialize()

        self.assertEquals(result, data)

    def test_collections_of_collections(self):
        class Outer(Serializer):
            rooms = Field(types.Collection(types.Collection(types.Integer())))

        data = {'rooms': [[1, 2, 3], [4, 5, 6]]}

        result = Outer(data).serialize()

        self.assertEquals(result, data)
