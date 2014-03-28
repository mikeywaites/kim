from .mapping import Mapping, marshal


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


from .types import String, Integer, Nested, Collection

data = TheData()

# inner_inner_mapping = Mapping('inner_2', String('e'))
# inner_mapping = Mapping('inner_mapping', String('d'), Nested('nested_two', mapped=inner_inner_mapping))
# the_mapping = Mapping(
#     'the_mapping',
#     String('a'),
#     Integer('b'),
#     Nested('c', mapped=inner_mapping),
#     Collection('l', Integer),
#     Collection('nested_list', Nested, mapped=inner_mapping),
# )

# print marshal(the_mapping, data)


from .serializers import Serializer, Field

class NestedSerializer(Serializer):
    d = Field(String)

class ProperSerializer(Serializer):
    a = Field(Integer)
    b = Field(String)
    c = Field(Nested, mapped=NestedSerializer)
    l = Field(Collection, member_type=Integer)
    nested_list = Field(Collection, member_type=Nested, mapped=NestedSerializer)

print marshal(ProperSerializer.__mapping__, data)