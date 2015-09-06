import pytest

from kim import Mapper, field

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
    data = {'post_ids': 1}

    with pytest.raises(field.FieldInvalid):
        f.marshal(data, output)


def test_serialize_collection_requires_list():

    f = field.Collection(field.Integer(), name='post_ids')
    output = {}
    data = {'post_ids': 1}

    with pytest.raises(field.FieldInvalid):
        f.marshal(data, output)
        f.serialize(data, output)


def test_marshal_flat_collection():

    f = field.Collection(field.Integer(), name='post_ids', source='posts')
    output = {}
    data = {
        'post_ids': [2, 1]
    }
    f.marshal(data, output)
    assert output == {'posts': [2, 1]}


def test_serialize_flat_collection():

    f = field.Collection(field.Integer(), name='post_ids', source='posts')
    output = {}
    data = {
        'posts': [2, 1]
    }
    f.serialize(data, output)
    assert output == {'post_ids': [2, 1]}


def test_marshal_read_only_collection():

    f = field.Collection(field.Integer(), name='post_ids', read_only=True)
    output = {}
    data = {
        'post_ids': [2, 1]
    }
    f.marshal(data, output)
    assert output == {}


def test_marshal_nested_collection():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True)
        name = field.String()
    data = {'id': 2, 'name': 'bob', 'users': [{'id': '1', 'name': 'mike'}]}

    f = field.Collection(field.Nested('UserMapper'), name='users')
    output = {}
    f.marshal(data, output)
    assert output == {'users': [TestType(id='1', name='mike')]}


def test_serialize_nested_collection():

    class UserMapper(Mapper):

        __type__ = TestType

        id = field.String(required=True, read_only=True)
        name = field.String()

    users = [TestType(id='1', name='mike'), TestType(id='2', name='jack')]
    post = TestType(id='1', users=users)

    output = {}
    f = field.Collection(field.Nested('UserMapper'), name='users')
    f.serialize(post, output)

    assert output == {'users': [{'id': '1', 'name': 'mike'},
                                {'id': '2', 'name': 'jack'}]}
