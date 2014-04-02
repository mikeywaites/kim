from .mapping import Mapping, serialize, marshal


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


from .types import String, Integer, Nested, MappedCollectionType, MappedType

data = TheData()

inner_inner_mapping = Mapping('inner_2', MappedType('e', String()))
inner_mapping = Mapping('inner_mapping', MappedType('d', String()), MappedType('nested_two', Nested(mapped=inner_inner_mapping)))
the_mapping = Mapping(
    'the_mapping',
    MappedType('a', String()),
    MappedType('b', Integer()),
    MappedType('c', Nested(mapped=inner_mapping)),
    MappedCollectionType('l', Integer()),
    MappedCollectionType('nested_list', Nested(mapped=inner_mapping)),
)

#print serialize(the_mapping, data)


from .serializers import Serializer, Field, Collection

class NestedSerializer(Serializer):
    d = Field(String)

class ProperSerializer(Serializer):
    a = Field(Integer)
    b = Field(String, name='hey', source='b')
    c = Field(Nested(mapped=NestedSerializer))
    l = Collection(Integer)
    nested_list = Collection(Nested(mapped=NestedSerializer))

from pprint import pprint
pprint(serialize(ProperSerializer.__mapping__, data))
print "===================="
pprint(marshal(ProperSerializer.__mapping__, data))
