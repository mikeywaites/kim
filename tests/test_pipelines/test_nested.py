import pytest

from kim.mapper import Mapper, MapperError
from kim.field import FieldInvalid
from kim import field


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

        id = field.String(required=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user')

    output = {}
    test_field.marshal(data, output)
    assert output == {'user': {'id': '1', 'name': 'mike'}}


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


def test_marshal_nested_with_read_only_field():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user')

    output = {}
    test_field.marshal(data, output)
    assert output == {'user': {'name': 'mike'}}


def test_marshal_read_only_nested_mapper():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user', read_only=True)

    output = {}
    test_field.marshal(data, output)
    assert output == {}


def test_marshal_nested_with_getter():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    users = {
        '1': {'id': '1', 'name': 'mike'},
        '2': {'id': '2', 'name': 'jack'}
    }

    def getter(field, data):
        return users[data['id']]

    test_field = field.Nested('UserMapper', name='user', getter=getter)

    data1 = {'id': 2, 'name': 'bob', 'user': {'id': '1'}}
    output = {}
    test_field.marshal(data1, output)
    assert output == {'user': {'id': '1', 'name': 'mike'}}

    data2 = {'id': 2, 'name': 'bob', 'user': {'id': '2'}}
    output = {}
    test_field.marshal(data2, output)
    assert output == {'user': {'id': '2', 'name': 'jack'}}


def test_marshal_nested_with_getter_failure():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    def getter(field, data):
        return None

    test_field = field.Nested('UserMapper', name='user', getter=getter)

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1'}}
    output = {}
    with pytest.raises(FieldInvalid):
        test_field.marshal(data, output)
