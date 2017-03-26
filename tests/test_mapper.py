import pytest

from six import get_unbound_function

from kim.exception import MapperError, MappingInvalid
from kim.mapper import (
    Mapper, _MapperConfig, get_mapper_from_registry, PolymorphicMapper)
from kim.field import Field, String, Integer, Nested, Collection
from kim.role import whitelist, blacklist
from kim.pipelines import marshaling, serialization, Pipe

from .fixtures import SchedulableMapper, EventMapper, TaskMapper


class TestType(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class IterableTestType(object):
    """This test type mimics constructs like SQA's result class or
    declarative_base objects that support iteration that enables access to
    attributes.
    """
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def keys(self):
        return self.kwargs.keys()


class TestField(Field):
    pass


def test_mapper_sets_fields():
    """Ensure that on attributes inheriting from :class:`kim.fields.Field`
    are set in a mappers fields.
    """

    class MyTestMapper(Mapper):

        __type__ = TestType

        name = TestField()
        other = 'not a field'

    mapper_with_fields = MyTestMapper(data={})
    assert 'name' in mapper_with_fields.fields
    assert isinstance(mapper_with_fields.fields['name'], TestField)
    assert 'other' not in mapper_with_fields.fields
    assert not getattr(mapper_with_fields, 'name', False)


def test_mapper_must_define_mapper_type():
    """Ensure that a :class:`.MapperError` is raised if a :class:`.Mapper`
    fails to set its __type__ attr.
    """

    mapper = Mapper(data={})
    with pytest.raises(MapperError):
        mapper._get_mapper_type()


def test_mapper_inheritance():
    """test inheriting from other mapper classes
    """

    class OtherField(Field):
        pass

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

    class NewMapper(MapperBase):

        __type__ = TestType

        id = OtherField()
        additional_field = TestField()

    mapper = MapperBase(data={})
    other_mapper = NewMapper(data={})

    assert len(mapper.fields.keys()) == 2
    assert 'id' in mapper.fields
    assert 'name' in mapper.fields

    assert len(other_mapper.fields.keys()) == 3
    assert 'id' in other_mapper.fields
    assert 'name' in other_mapper.fields
    assert 'additional_field' in other_mapper.fields

    assert isinstance(other_mapper.fields['id'], OtherField)


def test_get_mapper_type():
    """ensure the correct object is returned when acessing the Mapper.__type__
    via :meth:``_get_mapper_type``
    """

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()

    mapper = MapperBase(data={})
    assert mapper._get_mapper_type() == TestType


def test_order_of_fields():
    """ensure fields set by mapper metaclass are set in order
    using _creation_order
    """

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

    class MyMapper(MapperBase):

        email = TestField()

    class ThirdMapper(MyMapper):

        id = TestField()
        id._creation_order = 999

    mapper = MyMapper(data={})
    assert ['id', 'name', 'email'] == list(mapper.fields.keys())

    mapper = ThirdMapper(data={})
    assert ['name', 'email', 'id'] == list(mapper.fields.keys())


def test_override_default_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

        __roles__ = {
            '__default__': whitelist('id', )
        }

    mapper = MapperBase(data={})
    assert mapper.roles == {'__default__': whitelist('id', )}


def test_inherit_parent_roles():

    class RoleMixin(object):

        __roles__ = {
            'id_only': ['id', ]
        }

    class Parent(Mapper, RoleMixin):

        __type__ = TestType

        id = TestField()
        name = TestField()

        __roles__ = {
            'parent': ['name'],
            'overview': ['id', 'name']
        }

    class Child(Parent):

        __type__ = TestType

        __roles__ = {
            'overview': ['name', ]
        }

    mapper = Child(data={})
    assert mapper.roles == {
        '__default__': whitelist('id', 'name'),
        'overview': whitelist('name', ),
        'parent': whitelist('name', ),
        'id_only': whitelist('id', ),
    }


def test_new_mapper_sets_roles():

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

    class MyMapper(MapperBase):

        email = TestField()

        __roles__ = {
            'overview': ['email', ]
        }

    class OtherMapper(MyMapper):

        __roles__ = {
            'private': ['id', ]
        }

    mapper = MapperBase(data={})
    assert mapper.roles == {'__default__': whitelist('id', 'name')}

    mapper = MyMapper(data={})
    assert mapper.roles == {
        'overview': whitelist('email', ),
        '__default__': whitelist('id', 'name', 'email')}

    mapper = OtherMapper(data={})
    assert mapper.roles == {
        '__default__': whitelist('id', 'name', 'email'),
        'overview': whitelist('email'),
        'private': whitelist('id', )
    }


def test_polymorphic_mappers_role_inheritance():

    class MapperA(PolymorphicMapper):

        __type__ = TestType
        id = Integer()
        name = String()
        object_type = String()

        __roles__ = {
            '__default__': whitelist('id'),
            'overview': whitelist('id', 'name', 'object_type'),
        }

        __mapper_args__ = {
            'polymorphic_on': 'object_type',
        }

    class MapperB(MapperA):

        __roles__ = {
            '__default__': whitelist('id', 'name'),
            'type': whitelist('object_type'),
        }

        __mapper_args__ = {
            'polymorphic_name': 'B',
        }

    mapper = MapperA(data={})
    assert mapper.roles == {
        '__default__': whitelist('id'),
        'overview': whitelist('id', 'name', 'object_type')
    }

    mapperb = MapperB(data={})
    assert mapperb.roles == {
        '__default__': whitelist('id', 'name'),
        'overview': whitelist('id', 'name', 'object_type'),
        'type': whitelist('object_type'),
    }


def test_mapper_sets_field_names():

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        named = TestField(name='other_name')
        name = TestField(attribute_name='my_name')

    mapper = MapperBase(data={})
    assert mapper.fields['id'].opts.name == 'id'
    assert mapper.fields['name'].opts.name == 'my_name'
    assert mapper.fields['named'].opts.name == 'other_name'


def test_mapper_must_pass_obj_or_data():
    with pytest.raises(MapperError):
        Mapper()


def test_mapper_serialize():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj)
    result = mapper.serialize()

    assert result == {'id': 2, 'name': 'bob'}


def test_mapper_serialize_raw_standard_obj():
    """Ensure we can still serialize a mapper  with raw=True when the object
    has standardly named field names, IE no __dunder__
    """

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = IterableTestType(id=2, name='bob')

    mapper = MapperBase(obj, raw=True)
    result = mapper.serialize()

    assert result == {'id': 2, 'name': 'bob'}


def test_mapper_serialize_raw():

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper)

    obj = IterableTestType(
        id=2, name='bob',
        user__id='foo',
        user__name='bar',
        user__company__name='baz',
        user__company__id='bin')

    obj = IterableTestType(id=2, name='bob', user__id='foo', user__name='bar')
    mapper = MapperBase(obj, raw=True)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'user': {
            'id': 'foo',
            'name': 'bar'
        }
    }


def test_mapper_serialize_raw_nested_nested():

    class CompanyMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()
        company = Nested(CompanyMapper)

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper)

    obj = IterableTestType(
        id=2, name='bob',
        user__id='foo',
        user__name='bar',
        user__company__name='baz',
        user__company__id='bin')

    mapper = MapperBase(obj, raw=True)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'user': {
            'id': 'foo',
            'name': 'bar',
            'company': {
                'id': 'bin',
                'name': 'baz'
            }
        }
    }


def test_mapper_serialize_empty_nested_sets_null_default():
    """Ensure that when when a nested mapper has no data, the defined
    null_default is returned in its place.

    """

    class CompanyMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()
        company = Nested(CompanyMapper)

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper, null_default={})

    user_type = TestType(id='3', name='foo')
    obj1 = TestType(id='2', name='foo', user=user_type)
    mapper = MapperBase(obj1)
    result = mapper.serialize()
    assert result == {
        'id': '2',
        'name': 'foo',
        'user': {
            'id': '3',
            'name': 'foo',
            'company': None
        }
    }

    obj2 = IterableTestType(id=2, name='bob', user__id='3', user__name='foo')

    mapper = MapperBase(obj2, raw=True)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'user': {
            'id': '3',
            'name': 'foo',
            'company': None
        }
    }


def test_serialize_empty_nested_nested():
    """Ensure that when when a nested mapper has no data, the defined
    null_default is returned in its place.

    """

    class CompanyMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()
        company = Nested(CompanyMapper)

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper, null_default={})

    obj1 = TestType(id='2', name='foo', user=None)
    mapper = MapperBase(obj1)
    result = mapper.serialize()
    assert result == {
        'id': '2',
        'name': 'foo',
        'user': {}
    }

    obj2 = IterableTestType(id=2, name='bob')

    mapper = MapperBase(obj2, raw=True)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'user': {}
    }


def test_mapper_serialize_many():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj1 = TestType(id=1, name='bob')
    obj2 = TestType(id=2, name='mike')

    result = MapperBase.many().serialize([obj1, obj2])

    assert result == [{'id': 1, 'name': 'bob'}, {'id': 2, 'name': 'mike'}]


def test_mapper_marshal_many():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = [{'name': 'mike', 'id': 1}, {'name': 'bob', 'id': 2}]

    result = MapperBase.many().marshal(data)

    assert len(result) == 2
    res1, res2 = result
    assert (res1.name, res1.id) == ('mike', 1)
    assert (res2.name, res2.id) == ('bob', 2)


def test_mapper_marshal_many_with_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

        __roles__ = {
            'private': blacklist('id')
        }

    data = [{'name': 'mike', 'id': 1}, {'name': 'bob', 'id': 2}]

    result = MapperBase.many().marshal(data, role='private')

    assert len(result) == 2
    res1, res2 = result
    assert getattr(res1, 'id', False) is False
    assert getattr(res2, 'id', False) is False
    assert res1.name == 'mike'
    assert res2.name == 'bob'


def test_mapper_serialize_many_with_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

        __roles__ = {
            'private': blacklist('id')
        }

    obj1 = TestType(id=1, name='bob')
    obj2 = TestType(id=2, name='mike')

    result = MapperBase.many().serialize([obj1, obj2], role='private')

    assert result == [{'name': 'bob'}, {'name': 'mike'}]


def test_mapper_serialize_with_role_str():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

        __roles__ = {
            'private': ['id', ]
        }

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj)
    result = mapper.serialize(role='private')

    assert result == {'id': 2}


def test_mapper_serialize_raw_with_role():

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

        __roles__ = {
            'private': whitelist('name')
        }

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper, role='private')

        __roles__ = {
            'private': whitelist('name', 'user')
        }

    obj = IterableTestType(id=2, name='bob', user__id='id', user__name='name')

    mapper = MapperBase(obj)
    result = mapper.serialize(role='private', raw=True)

    assert result == {'name': 'bob', 'user': {'name': 'name'}}


def test_mapper_marshal_with_role_str():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

        __roles__ = {
            'private': ['id', ]
        }

    data = {'name': 'mike', 'id': 3}
    mapper = MapperBase(data=data)
    result = mapper.marshal(role='private')

    assert result.id == 3


def test_mapper_marshal_with_empty_nested():

    class UserMapper(Mapper):

        __type__ = TestType

        id = String(required=True, read_only=True)
        name = String()

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper, role='private')

        __roles__ = {
            'private': ['id', ]
        }

    data = {'name': 'mike', 'id': 3}
    mapper = MapperBase(data=data)
    result = mapper.marshal(role='private')

    assert getattr(result, 'user', None) is None


def test_mapper_serialize_with_role_as_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj)
    result = mapper.serialize(role=blacklist('id'))

    assert result == {'name': 'bob'}


def test_mapper_marshal_with_role_as_role():

    class MyType(TestType):

        def __init__(self, **params):
            self.id = 2
            super(MyType, self).__init__(**params)

    class MapperBase(Mapper):

        __type__ = MyType

        id = Integer()
        name = String()

    data = {'name': 'mike', 'id': 3}
    mapper = MapperBase(data=data)
    obj = mapper.marshal(role=blacklist('id'))

    assert obj.name == 'mike'
    assert obj.id == 2


def test_mapper_serialize_with_invalid_role_type():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj)

    with pytest.raises(MapperError):
        mapper.serialize(role=object())


def test_mapper_marshal_with_invalid_role_type():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj)

    with pytest.raises(MapperError):
        mapper.marshal(role=object())


def test_mapper_marshal():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'id': 2, 'name': 'bob'}

    mapper = MapperBase(data=data)
    result = mapper.marshal()

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'


def test_get_fields_with_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

        __roles__ = {
            'private': ['id', ]
        }

    data = {'id': 2, 'name': 'bob'}
    mapper = MapperBase(data=data)
    fields = mapper._get_fields('private')
    assert [MapperBase.fields['id'], ] == fields


def test_get_fields_with_invalid_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'id': 2, 'name': 'bob'}
    mapper = MapperBase(data=data)
    with pytest.raises(MapperError):
        mapper._get_fields('invalid')


def test_mapper_with_invalid_role_type():

    with pytest.raises(MapperError):
        class MapperBase(Mapper):

            __type__ = TestType

            id = Integer()
            name = String()

            __roles__ = {
                'public': object()
            }


def test_mapper_marshal_update():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'id': 2, 'name': 'bob'}
    obj = TestType(unrelated_attribute='test')

    mapper = MapperBase(obj=obj, data=data)
    result = mapper.marshal()

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'
    assert result.unrelated_attribute == 'test'


def test_mapper_registered_in_class_registry():

    class MapperBase(Mapper):

        __type__ = TestType
        id = Integer()
        name = String()

    assert 'MapperBase' in _MapperConfig.MAPPER_REGISTRY


def test_polymorphic_mapper_sets_identities():

    assert SchedulableMapper._polymorphic_identities == {
        'event': EventMapper,
        'task': TaskMapper
    }


def test_polymorphic_mapper_returns_correct_mapper():

    obj = TestType(id=2, name='bob', object_type='event')
    mapper = SchedulableMapper(obj=obj)
    assert isinstance(mapper, EventMapper)


def test_polymorphic_mapper_missing_identity():

    obj = TestType(id=2, name='bob', object_type='review')
    with pytest.raises(MapperError):
        SchedulableMapper(obj=obj)


def test_polymorphic_on_with_string():

    class MapperA(PolymorphicMapper):

        __type__ = TestType
        id = Integer()
        name = String()
        object_type = String()

        __mapper_args__ = {
            'polymorphic_on': 'object_type',
        }

    class MapperB(MapperA):

        __mapper_args__ = {
            'polymorphic_name': 'B',
        }

    mapper = MapperA(data={})
    assert isinstance(
        mapper._polymorphic_opts['polymorphic_on'], Field)


def test_mapper_already_registered():

    class MapperOne(Mapper):

        __type__ = TestType
        id = Integer()
        name = String()

    def create_mapper():
        class MapperOne(Mapper):

            __type__ = TestType
            id = Integer()
            name = String()

    with pytest.raises(MapperError):
        create_mapper()


def test_get_mapper_from_registry_str_name():
    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

    mapper = get_mapper_from_registry('UserMapper')
    assert mapper == UserMapper


def test_get_mapper_from_registry_mapper_type():

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True, read_only=True)
        name = String()

    mapper = get_mapper_from_registry(UserMapper)
    assert mapper == UserMapper


def test_get_mapper_from_registry_mapper_does_not_exist():

    with pytest.raises(MapperError):
        get_mapper_from_registry('OtherMapper')


def test_mapper_with_invalid_fields_sets_errors():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'id': 'abc', 'name': 'bob'}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()

    assert mapper.errors == {'id': 'Invalid type'}


def test_mapper_with_invalid_nested_fields_sets_errors():

    class UserMapper(Mapper):

        __type__ = dict

        id = String()
        name = String()

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        user = Nested(UserMapper, allow_create=True)

    data = {'id': 1, 'name': 'bob', 'user': {'name': 1}}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()

    assert mapper.errors == {'user': {'id': 'This is a required field'}}


def test_mapper_with_invalid_collection_fields_sets_errors():

    class UserMapper(Mapper):

        __type__ = dict

        id = String(required=True)
        name = String()

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        users = Collection(Nested(UserMapper, allow_create=True))

    data = {'id': 1, 'name': 'bob',
            'users': [{'name': 1, 'id': 'foo'}, {'name': 1}]}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()

    assert mapper.errors == {'users': {'id': 'This is a required field'}}
