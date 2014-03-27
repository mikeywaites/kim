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


from .types import String, Integer, Nested

data = TheData()

inner_inner_mapping = Mapping('inner_2', String('e'))
inner_mapping = Mapping('inner_mapping', String('d'), Nested('nested_two', mapped=inner_inner_mapping))
the_mapping = Mapping('the_mapping', String('a'), Integer('b'), Nested('c', mapped=inner_mapping))

print marshal(the_mapping, data)
