from kim import Mapper, field


class ChildTestObject(object):
    def __init__(self, multiplier=None):
        self.w = 1000 * multiplier if multiplier else 100
        self.x = 20 * multiplier if multiplier else 20
        self.y = 'hello' * multiplier if multiplier else 'hello'
        self.z = 10 * multiplier if multiplier else 10


class ParentTestObject(object):
    def __init__(self):
        self.foo = 'bar'
        self.sub = ChildTestObject()
        self.subs = [ChildTestObject(i) for i in range(10)]

    def bar(self):
        return 5


class Complex(object):
    pass


class SubResource(object):
    pass


def bar_pipe(session):
    session.output['bar'] = session.data()


def x_pipe(session):
    session.output['x'] = session.data + 10


class SubMapper(Mapper):
        __type__ = SubResource
        w = field.String()
        x = field.String(extra_serialize_pipes={'output': [x_pipe]})
        y = field.String()
        z = field.String()


class ComplexMapper(Mapper):
        __type__ = Complex
        foo = field.String()
        bar = field.String(extra_serialize_pipes={'output': [bar_pipe]})
        sub = field.Nested(SubMapper)
        subs = field.Collection(field.Nested(SubMapper))


def serialize(data, many=False):

    if many:
        return ComplexMapper.many().serialize(data)
    else:
        ComplexMapper(obj=data).serialize()


test_object = ParentTestObject()
