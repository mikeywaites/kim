from .mapping import Mapping, marshal

class InnerData(object):
    d = 'nested!'


class TheData(object):
    a = 324
    b = 'hello'
    c = InnerData()


from .types import String, Integer, Nested

data = TheData()

inner_mapping = Mapping('inner_mapping', String('d'))
the_mapping = Mapping('the_mapping', String('a'), Integer('b'), Nested('c', mapped=inner_mapping))

print marshal(the_mapping, data)