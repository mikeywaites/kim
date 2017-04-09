import pytest

from kim.mapper import Mapper, MapperError
from kim.field import FieldInvalid
from kim import field
from kim.pipelines import marshaling

from ..conftest import get_mapper_session
from ..helpers import TestType


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
    test_field = field.Nested('UserMapper', name='user', allow_create=True)

    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'mike'}}


def test_serialise_nested():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user')

    output = {}
    mapper_session = get_mapper_session(obj=data, output=output)
    test_field.serialize(mapper_session)
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
    mapper_session = get_mapper_session(obj=data, output=output)
    test_field.serialize(mapper_session)
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
    test_field = field.Nested('UserMapper', name='user', role='public',
                              allow_create=True)

    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'name': 'mike'}}


def test_marshal_nested_with_read_only_field():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user', allow_create=True)

    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'name': 'mike'}}


def test_marshal_read_only_nested_mapper():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True, read_only=True)
        name = field.String()

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1', 'name': 'mike'}}
    test_field = field.Nested('UserMapper', name='user', read_only=True)

    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    test_field.marshal(mapper_session)
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

    def getter(session):
        return users[session.data['id']]

    test_field = field.Nested('UserMapper', name='user', getter=getter)

    data1 = {'id': 2, 'name': 'bob', 'user': {'id': '1'}}
    output = {}
    mapper_session = get_mapper_session(data=data1, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'mike'}}

    data2 = {'id': 2, 'name': 'bob', 'user': {'id': '2'}}
    output = {}
    mapper_session = get_mapper_session(data=data2, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '2', 'name': 'jack'}}


def test_marshal_nested_with_getter_failure():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    def getter(session):
        return None

    test_field = field.Nested('UserMapper', name='user', getter=getter)

    data = {'id': 2, 'name': 'bob', 'user': {'id': '1'}}
    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    with pytest.raises(FieldInvalid):
        test_field.marshal(mapper_session)


def test_marshal_nested_with_defaults():
    # Users may only be passed by id and may not be updated

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    user = {'id': '1', 'name': 'mike'}

    def getter(session):
        return user

    test_field = field.Nested('UserMapper', name='user', getter=getter)

    data1 = {'id': 2, 'name': 'bob', 'user': {
        'id': '1', 'name': 'this should be ignored'}}
    output = {}
    mapper_session = get_mapper_session(data=data1, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'mike'}}

    assert user['name'] == 'mike'


def test_marshal_nested_with_allow_updates():
    # Users may only be passed by id and may be updated, but not created

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    user = {'id': '1', 'name': 'mike'}

    def getter(session):
        if session.data['id'] == '1':
            return user

    test_field = field.Nested('UserMapper', name='user', getter=getter,
                              allow_updates=True)

    data1 = {'id': 2, 'name': 'bob', 'user': {
        'id': '1', 'name': 'a new name'}}
    output = {}
    mapper_session = get_mapper_session(data=data1, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'a new name'}}
    assert user['name'] == 'a new name'

    data2 = {'id': 2, 'name': 'bob', 'user': {
        'id': '2', 'name': 'should not allow this to be created'}}
    output = {}
    mapper_session = get_mapper_session(data=data2, output=output)
    with pytest.raises(FieldInvalid):
        test_field.marshal(mapper_session)


def test_marshal_nested_with_allow_create_only():
    # Users may only be passed by id or created if they don't exist

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    user = {'id': '1', 'name': 'mike'}

    def getter(session):
        if session.data['id'] == '1':
            return user

    test_field = field.Nested('UserMapper', name='user', getter=getter,
                              allow_create=True)

    data1 = {'id': 2, 'name': 'bob', 'user': {
        'id': '1', 'name': 'this should be ignored'}}
    output = {}
    mapper_session = get_mapper_session(data=data1, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'mike'}}

    assert user['name'] == 'mike'

    data2 = {'id': 2, 'name': 'bob', 'user': {
        'id': '2', 'name': 'jack'}}
    output = {}
    mapper_session = get_mapper_session(data=data2, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '2', 'name': 'jack'}}


def test_marshal_nested_with_allow_create_and_allow_updates():
    # Users may only be passed by id or created if they don't exist and
    # updated

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    user = {'id': '1', 'name': 'mike'}

    def getter(session):
        if session.data['id'] == '1':
            return user

    test_field = field.Nested('UserMapper', name='user', getter=getter,
                              allow_create=True, allow_updates=True)

    data1 = {'id': 2, 'name': 'bob', 'user': {
        'id': '1', 'name': 'a new name'}}
    output = {}
    mapper_session = get_mapper_session(data=data1, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'a new name'}}
    assert user['name'] == 'a new name'

    data2 = {'id': 2, 'name': 'bob', 'user': {
        'id': '2', 'name': 'jack'}}
    output = {}
    mapper_session = get_mapper_session(data=data2, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '2', 'name': 'jack'}}


def test_marshal_nested_with_allow_updates_in_place():
    # No getter required, but the existing user object can be changed

    class UserMapper(Mapper):

        __type__ = dict

        name = field.String()

    user = {'id': '1', 'name': 'mike'}
    output = {'user': user}

    test_field = field.Nested('UserMapper', name='user',
                              allow_updates_in_place=True)

    data1 = {'id': 2, 'name': 'bob', 'user': {'name': 'a new name'}}
    mapper_session = get_mapper_session(data=data1, output=output)
    test_field.marshal(mapper_session)
    assert output == {'user': {'id': '1', 'name': 'a new name'}}
    assert user['name'] == 'a new name'


def test_marshal_nested_partial():

    class UserMapper(Mapper):

        __type__ = dict

        id = field.String(required=True)
        name = field.String()

    class DocumentMapper(Mapper):
        __type__ = dict

        id = field.String(required=True)
        name = field.String()
        user = field.Nested('UserMapper', name='user',
                            allow_partial_updates=True)

    obj = {'id': 2, 'name': 'my document', 'user': {
        'id': '1', 'name': 'existing name'}}

    data = {'name': 'new name', 'user': {'name': 'new user name'}}

    mapper = DocumentMapper(obj=obj, data=data, partial=True)

    mapper.marshal()

    assert obj['name'] == 'new name'
    assert obj['user']['name'] == 'new user name'


def test_self_nesting_marshal():
    class Inner(Mapper):
        __type__ = dict

        name = field.String(source='user_name')

    class Outer(Mapper):
        __type__ = dict

        user = field.Nested(Inner, source='__self__', allow_create=True)
        status = field.Integer()

    data = {'user': {'name': 'jack'}, 'status': 200}

    result = Outer(data=data).marshal()

    assert result == {'user_name': 'jack', 'status': 200}
