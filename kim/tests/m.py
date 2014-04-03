from ..mapping import Mapping, serialize, marshal


class OtherInner(object):
    e = 'inner nested'


class InnerData(object):
    d = 'nested!'
    nested_two = OtherInner()


class TheData(object):
    a = 324
    b = 'hello'
    c = InnerData()
    l = [1, 2, 3]
    nested_list = [InnerData(), InnerData()]


from ..types import String, Integer, Nested, CollectionTypeMapper, TypeMapper

data = TheData()

inner_inner_mapping = Mapping(TypeMapper('e', String()))
inner_mapping = Mapping(TypeMapper('d', String()), TypeMapper('nested_two', Nested(mapped=inner_inner_mapping)))
the_mapping = Mapping(
    TypeMapper('a', String()),
    TypeMapper('b', Integer()),
    TypeMapper('c', Nested(mapped=inner_mapping)),
    CollectionTypeMapper('l', Integer()),
    CollectionTypeMapper('nested_list', Nested(mapped=inner_mapping)),
)

#print serialize(the_mapping, data)


from ..serializers import Serializer, Field, Collection

class NestedSerializer(Serializer):
    d = Field(String)

class ProperSerializer(Serializer):
    a = Field(Integer)
    b = Field(String, name='hey', source='b')
    c = Field(Nested(mapped=NestedSerializer))
    l = Collection(Integer)
    nested_list = Collection(Nested(mapped=NestedSerializer))

from pprint import pprint
result = serialize(ProperSerializer.__mapping__, data)
pprint(result)
result['b'] = result['hey']
print "===================="
pprint(marshal(ProperSerializer.__mapping__, result))
