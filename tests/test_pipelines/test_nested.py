import pytest

from kim.mapper import Mapper, MapperError
from kim import field


class TestType(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_nested_defers_mapper_checks():
    """ensure that instantiating a nested field with an invalid mapper
    doesn't emit an error until the nested mapper is actually needed.

    """
    field.Nested('IDontExist', name='user')


def test_nested_get_mapper_str_mapper_name():
    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    f = field.Nested('UserMapper', name='user')
    assert isinstance(f.get_mapper(data={'foo': 'id'}), UserMapper)


def test_get_mapper_mapper_type():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    f = field.Nested(UserMapper, name='user')
    assert isinstance(f.get_mapper(data={'foo': 'id'}), UserMapper)


def test_get_mapper_not_registered():

    f = field.Nested('UserMapper', name='user')
    with pytest.raises(MapperError):
        f.get_mapper(data={'foo': 'id'})


def test_get_mapper_not_a_valid_mapper():

    class Foo(object):
        pass

    f = field.Nested(Foo, name='user')
    with pytest.raises(MapperError):
        f.get_mapper(data={'foo': 'id'})


def test_marshal_nested():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user')

    output = {}
    test_field.marshal(data, output)
    assert output == {'user': {'id': '1', 'name': 'mike'}}


def test_marshal_many_nested():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {
        'id': 2,
        'name': 'bob',
        'users': [
            {'id': '1', 'name': 'mike'},
            {'id': '2', 'name': 'bob'}
        ]
    }
    test_field = field.Nested('UserMapper', name='users', many=True)

    output = {}
    test_field.marshal(data, output)
    assert output == {'users': data['users']}


def test_serialise_nested():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user')

    output = {}
    test_field.serialize(data, output)
    assert output == {'user': {'id': '1', 'name': 'mike'}}


def test_serialize_many_nested():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {
        'id': 2,
        'name': 'bob',
        'users': [
            {'id': '1', 'name': 'mike'},
            {'id': '2', 'name': 'bob'}
        ]
    }
    test_field = field.Nested('UserMapper', name='users', many=True)

    output = {}
    test_field.serialize(data, output)
    assert output == {'users': data['users']}


def test_serialise_nested_with_role():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user', role='public')

    output = {}
    test_field.serialize(data, output)
    assert output == {'user': {'name': 'mike'}}


def test_serialise_many_nested_with_role():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    data = {
        'id': 2,
        'name': 'bob',
        'users': [
            {'id': '1', 'name': 'mike'},
            {'id': '2', 'name': 'bob'}
        ]
    }
    test_field = field.Nested('UserMapper', many=True, name='users', role='public')

    output = {}
    test_field.serialize(data, output)
    assert output == {'users': [{'name': 'mike'}, {'name': 'bob'}]}


def test_marshal_nested_with_role():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user', role='public')

    output = {}
    test_field.marshal(data, output)
    assert output == {'user': {'name': 'mike'}}


def test_marshal_many_nested_with_role():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    data = {
        'id': 2,
        'name': 'bob',
        'users': [
            {'id': '1', 'name': 'mike'},
            {'id': '2', 'name': 'bob'}
        ]
    }
    test_field = field.Nested('UserMapper', many=True, name='users', role='public')

    output = {}
    test_field.marshal(data, output)
    assert output == {'users': [{'name': 'mike'}, {'name': 'bob'}]}
