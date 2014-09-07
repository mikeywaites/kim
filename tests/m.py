from kim.mapping import Mapping, serialize, marshal
from datetime import date


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
    when = date(2014, 4, 7)


from ..types import String, Integer, Nested, Collection, Date
from ..type_mapper import TypeMapper

data = TheData()

inner_inner_mapping = Mapping(TypeMapper('e', String()))
inner_mapping = Mapping(TypeMapper('d', String()), TypeMapper('nested_two', Nested(mapped=inner_inner_mapping)))
the_mapping = Mapping(
    TypeMapper('a', Integer()),
    TypeMapper('b', String()),
    TypeMapper('c', Nested(mapped=inner_mapping)),
    TypeMapper('l', Collection(Integer())),
    TypeMapper('nested_list', Collection(Nested(mapped=inner_mapping))),
)
print serialize(the_mapping, data)


from ..serializers import Serializer, Field



class ProperSerializer(Serializer):
    a = Field(Integer)
    b = Field(String, name='hey', source='b')
    c = Field(Nested(mapped='NestedSerializer'))
    l = Field(Collection(Integer()))
    nested_list = Field(Collection(Nested(mapped='NestedSerializer')))
    when = Field(Date)


class NestedSerializer(Serializer):
    d = Field(String)
    nested_two = Field(Nested(mapped='kim.tests.m2.InnerNestedSerializer'))

from pprint import pprint
result = serialize(ProperSerializer.__mapping__, data)
pprint(result)
print "===================="
pprint(marshal(ProperSerializer.__mapping__, result))

print "===================="

result = ProperSerializer().serialize(data)
pprint(result)
print "===================="

result = ProperSerializer().marshal(result)
pprint(result)


# class BrokenSerializer(Serializer):
#     d = String()

result = ProperSerializer().serialize([data, data, data], many=True)
pprint(result)

result = ProperSerializer().marshal(result, many=True)
pprint(result)
