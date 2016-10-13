import pytest

from kim import Mapper, field
from kim.exception import MappingInvalid
from kim.field import FieldInvalid
from kim.pipelines import marshaling

from ..conftest import get_mapper_session
from ..helpers import TestType


def test_collection_proxies_name_to_wrapped_field():

    f = field.Collection(field.Integer(), name='post_ids')
    f2 = field.Collection(field.String(), name='test')

    with pytest.raises(field.FieldError):
        field.Collection(field.String(name='foo'))

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True)
        tags = field.Collection(field.String())

    assert f.name == 'post_ids'
    assert f2.name == 'test'

    mapper = UserMapper({})
    assert mapper.fields['tags'].name == 'tags'


def test_marshal_collection_requires_list():

    f = field.Collection(field.Integer(), name='post_ids')
    output = {}

    mapper_session = get_mapper_session(data={'post_ids': 1}, output=output)
    with pytest.raises(field.FieldInvalid):
        f.marshal(mapper_session)


def test_marshal_flat_collection():

    f = field.Collection(field.Integer(), name='post_ids', source='posts')
    output = {}
    data = {
        'post_ids': [2, 1]
    }
    mapper_session = get_mapper_session(data=data, output=output)
    f.marshal(mapper_session)
    assert output == {'posts': [2, 1]}


def test_serialize_flat_collection():

    f = field.Collection(field.Integer(), name='post_ids', source='posts')
    output = {}
    data = {
        'posts': [2, 1]
    }
    mapper_session = get_mapper_session(obj=data, output=output)
    f.serialize(mapper_session)
    assert output == {'post_ids': [2, 1]}


def test_marshal_read_only_collection():

    f = field.Collection(field.Integer(), name='post_ids', read_only=True)
    output = {}
    data = {
        'post_ids': [2, 1]
    }
    mapper_session = get_mapper_session(data=data, output=output)
    f.marshal(mapper_session)
    assert output == {}


def test_marshal_collection_collection_allow_create():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True)
        name = field.String()
    data = {'id': 2, 'name': 'bob', 'users': [{'id': '1', 'name': 'mike'}]}

    f = field.Collection(field.Nested('UserMapper', allow_create=True),
                         name='users')
    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    f.marshal(mapper_session)
    assert output == {'users': [TestType(id='1', name='mike')]}


def test_marshal_nested_collection_default():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True)
        name = field.String()

    user = TestType(id='1', name='mike')
    data = {'id': 2, 'name': 'bob', 'users': [{'id': '1',
                                              'name': 'ignore this'}]}

    def getter(session):
        if session.data['id'] == '1':
            return user

    f = field.Collection(field.Nested('UserMapper', getter=getter),
                         name='users')
    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    f.marshal(mapper_session)
    assert output == {'users': [user]}
    assert user.name == 'mike'


def test_marshal_nested_collection_allow_updates():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True)
        name = field.String()

    user = TestType(id='1', name='mike')
    data = {'id': 2, 'name': 'bob', 'users': [{'id': '1', 'name': 'new name'}]}

    def getter(session):
        if session.data['id'] == '1':
            return user

    f = field.Collection(field.Nested('UserMapper', getter=getter,
                         allow_updates=True), name='users')
    output = {}
    mapper_session = get_mapper_session(data=data, output=output)
    f.marshal(mapper_session)
    assert output == {'users': [user]}
    assert user.name == 'new name'


def test_marshal_nested_collection_allow_updates_in_place():

    class UserMapper(Mapper):

        __type__ = TestType

        name = field.String()

    user = TestType(id='1', name='mike')
    data = {'id': 2, 'name': 'bob', 'users': [{'name': 'new name'}]}

    f = field.Collection(field.Nested('UserMapper',
                         allow_updates_in_place=True), name='users')
    output = {'users': [user]}
    mapper_session = get_mapper_session(data=data, output=output)
    f.marshal(mapper_session)
    assert output == {'users': [user]}
    assert user.name == 'new name'


def test_marshal_nested_collection_allow_updates_in_place_too_many():
    # We're updating in place, but there are more users in the input data
    # than already exist so an error should be raised

    class UserMapper(Mapper):

        __type__ = TestType

        name = field.String()

    user = TestType(id='1', name='mike')
    data = {'id': 2, 'name': 'bob', 'users': [
        {'name': 'name1'}, {'name': 'name2'}]}

    f = field.Collection(field.Nested('UserMapper',
                         allow_updates_in_place=True), name='users')
    output = {'users': [user]}
    mapper_session = get_mapper_session(data=data, output=output)
    with pytest.raises(FieldInvalid):
        f.marshal(mapper_session)


def test_marshal_nested_collection_allow_updates_in_place_too_many_with_allow_create():
    # We're updating in place, there are more users in the input data
    # but allow_create is also enabled, so a new user should be added

    class UserMapper(Mapper):

        __type__ = TestType

        name = field.String()

    user = TestType(id='1', name='mike')
    data = {'id': 2, 'name': 'bob', 'users': [
        {'name': 'name1'}, {'name': 'name2'}]}

    f = field.Collection(field.Nested('UserMapper',
                         allow_updates_in_place=True, allow_create=True),
                         name='users')
    output = {'users': [user]}
    mapper_session = get_mapper_session(data=data, output=output)

    f.marshal(mapper_session)

    assert output == {
        'users': [TestType(id='1', name='name1'), TestType(name='name2')]}


def test_serialize_nested_collection():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()

    users = [TestType(id='1', name='mike'), TestType(id='2', name='jack')]
    post = TestType(id='1', users=users)

    output = {}
    f = field.Collection(field.Nested('UserMapper'), name='users')
    mapper_session = get_mapper_session(obj=post, output=output)
    f.serialize(mapper_session)

    assert output == {'users': [{'id': '1', 'name': 'mike'},
                                {'id': '2', 'name': 'jack'}]}


def test_collection_memoize_no_existing_value():
    """ensure field sets only the new_value when the field has no
    exsiting value.
    """

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()
        address = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    def user_getter(session):
        if session.data['id'] == 'xyz':
            return TestType(id='xyz', name='mike', address='london')
        if session.data['id'] == 'zyx':
            return TestType(id='zyx', name='jack', address='stevenage')

    class PostMapper(Mapper):

        __type__ = TestType
        name = field.String()
        readers = field.Collection(
            field.Nested('UserMapper', role='public',
                         getter=user_getter))

    output = TestType(**{
        'name': 'my post',
    })

    data = {
        'name': 'my post',
        'readers': [{
            'id': 'zyx',
            'name': 'jack',
            'address': 'london',
        }]
    }

    mapper = PostMapper(obj=output, data=data)
    mapper.marshal()
    old, new = (mapper.get_changes()['readers']['old_value'],
                mapper.get_changes()['readers']['new_value'])

    assert old is None
    assert new == [TestType(id='zyx', name='jack', address='stevenage')]


def test_collection_memoize_no_change():
    """ensure field sets only the new_value when the field has no
    exsiting value.
    """

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()
        address = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    def user_getter(session):
        if session.data['id'] == 'xyz':
            return TestType(id='xyz', name='mike', address='london')
        if session.data['id'] == 'zyx':
            return TestType(id='zyx', name='jack', address='stevenage')

    class PostMapper(Mapper):

        __type__ = TestType
        name = field.String()
        readers = field.Collection(
            field.Nested('UserMapper', role='public',
                         getter=user_getter))

    output = TestType(**{
        'name': 'my post',
        'readers': [TestType(**{
            'id': 'xyz',
            'name': 'mike',
            'address': 'london',
        })]
    })

    data = {
        'name': 'my post',
        'readers': [{
            'id': 'xyz',
            'name': 'mike',
            'address': 'london',
        }]
    }

    mapper = PostMapper(obj=output, data=data)
    mapper.marshal()
    assert 'readers' not in mapper.get_changes()


def test_collection_memoize_new_value():
    """ensure field sets only the new_value when the field has no
    exsiting value.
    """

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()
        address = field.String()

        __roles__ = {
            'public': ['name', ]
        }

    def user_getter(session):
        if session.data['id'] == 'xyz':
            return TestType(id='xyz', name='mike', address='london')
        if session.data['id'] == 'zyx':
            return TestType(id='zyx', name='jack', address='stevenage')

    class PostMapper(Mapper):

        __type__ = TestType
        name = field.String()
        readers = field.Collection(
            field.Nested('UserMapper', role='public',
                         getter=user_getter))

    output = TestType(**{
        'name': 'my post',
        'readers': [TestType(**{
            'id': 'xyz',
            'name': 'mike',
            'address': 'london',
        })]
    })

    data = {
        'name': 'my post',
        'readers': [{
            'id': 'zyx',
            'name': 'jack',
            'address': 'stevenage',
        }]
    }

    mapper = PostMapper(obj=output, data=data)
    mapper.marshal()
    old, new = (mapper.get_changes()['readers']['old_value'],
                mapper.get_changes()['readers']['new_value'])

    assert old == [TestType(id='xyz', name='mike', address='london')]
    assert new == [TestType(id='zyx', name='jack', address='stevenage')]


def test_marshal_collection_sets_parent_session_scope():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()

    def assert_scope(session):

        assert session.parent is not None
        assert isinstance(session.parent.output, TestType)

        return TestType(id=session.data['id'], name='foo')

    class PostMapper(Mapper):

        __type__ = TestType

        readers = field.Collection(field.Nested(UserMapper, getter=assert_scope))

    data = {'id': '1', 'readers': [{'id': '1', 'name': 'mike'}]}

    mapper = PostMapper(data=data)
    mapper.marshal()


def test_marshal_collection_inherits_parent_session_partial():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()

    def assert_scope(session):

        assert session.mapper_session.partial is True

        return TestType(id=session.data['id'], name='foo')

    class PostMapper(Mapper):

        __type__ = TestType

        readers = field.Collection(field.Nested(UserMapper, getter=assert_scope))

    data = {'id': '1', 'readers': [{'id': '1', 'name': 'mike'}]}

    mapper = PostMapper(data=data, partial=True)
    mapper.marshal()


def test_serialize_collection_sets_parent_session_scope():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()

    def assert_scope(session):

        assert session.parent is not None
        assert isinstance(session.parent.output, TestType)

        return TestType(id=session.data['id'], name='foo')

    class PostMapper(Mapper):

        __type__ = TestType

        readers = field.Collection(field.Nested(UserMapper, getter=assert_scope))

    users = [TestType(id='1', name='mike'), TestType(id='2', name='jack')]
    post = TestType(id='1', users=users)

    mapper = PostMapper(obj=post)
    mapper.serialize()


def test_marshal_nested_collection_sets_mapper_parent():

    data = {'id': '1', 'readers': [{'id': '1', 'name': 'mike'}]}

    called = {'called': False}

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()

        @marshaling.validates('name')
        def assert_parent(session):
            called['called'] = True
            assert session.mapper.parent is not None
            assert isinstance(session.mapper.parent, PostMapper)
            assert session.mapper.parent.data == data

    def user_getter(session):

        return TestType(id=session.data['id'], name='foo')

    class PostMapper(Mapper):

        __type__ = TestType

        readers = field.Collection(
            field.Nested(UserMapper, getter=user_getter, allow_updates=True))

    mapper = PostMapper(data=data)
    mapper.marshal()
    assert called['called']


def test_marshal_collection_unique_on():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True)
        name = field.String()

    class PostMapper(Mapper):

        __type__ = TestType

        readers = field.Collection(
            field.Nested(UserMapper, allow_create=True),
            unique_on='id')

    data = {
        'readers': [{'id': '1', 'name': 'jack'}, {'id': '1', 'name': 'jack'}]
    }

    mapper = PostMapper(data=data)

    with pytest.raises(MappingInvalid):
        mapper.marshal()

    # Check error not raised with valid data
    data = {
        'readers': [{'id': '1', 'name': 'jack'}, {'id': '2', 'name': 'mike'}]
    }

    mapper = PostMapper(data=data)
    mapper.marshal()
