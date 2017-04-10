import pytest

from kim.field import Field, FieldInvalid, FieldError
from kim.pipelines.base import (
    Session,
    get_data_from_source, get_data_from_name, update_output_to_name,
    update_output_to_source)


def test_get_data_from_name_pipe():

    data = {
        'name': 'mike',
        'test': 'true',
        'falsy': 0,
        'nested': {'foo': 'bar'}
    }

    default = 'bar'
    field = Field(name='foo', required=True)
    field2 = Field(name='foo', default=default, required=False)
    field3 = Field(name='foo', allow_none=False, required=False)
    field4 = Field(name='falsy', required=True)
    field5 = Field(name='falsy', allow_none=False)

    # Required but not present and no default
    output = {}
    session = Session(field, data, output)
    with pytest.raises(FieldInvalid):
        get_data_from_name(session)

    # Not present but default set
    session = Session(field2, data, output)
    assert get_data_from_name(session) == default

    # Not present and none not allowed
    session = Session(field3, data, output)
    with pytest.raises(FieldInvalid):
        get_data_from_name(session)

    # Required, value present and falsy - should still be allowed
    session = Session(field4, data, output)
    assert get_data_from_name(session) == 0

    # None not allowed, value present and falsy - should still be allowed
    session = Session(field5, data, output)
    assert get_data_from_name(session) == 0


def test_get_data_from_source_pipe():
    data = {
        'name': 'mike'
    }
    output = {}

    field = Field(source='foo')
    session = Session(field, data, output)
    assert get_data_from_source(session) is None

    field = Field(source='name')
    session = Session(field, data, output)
    assert get_data_from_source(session) == 'mike'


def test_get_data_from_source_pipe_dot_syntax():
    data = {
        'user': {
            'name': 'mike'
        }
    }
    output = {}

    field = Field(source='foo.bar')
    session = Session(field, data, output)
    assert get_data_from_source(session) is None

    field = Field(source='user.name')
    session = Session(field, data, output)
    assert get_data_from_source(session) == 'mike'


def test_get_data_from_source_pipe_self():
    data = {
        'name': 'mike'
    }
    output = {}

    field = Field(source='__self__')
    session = Session(field, data, output)
    assert get_data_from_source(session) is data


def test_update_output_to_name_with_dict():

    data = {
        'name': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    output = {}

    field = Field(name='name', required=True)
    session = Session(field, data, output)
    session.data = data['name']
    update_output_to_name(session)
    assert output == {'name': 'mike'}


def test_update_output_to_source_with_object():

    data = {
        'source': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    class MyObject(object):
        pass

    output = MyObject()
    field = Field(source='source', required=True)
    session = Session(field, data, output)
    session.data = data['source']

    update_output_to_source(session)
    assert output.source == 'mike'


def test_update_output_to_source_with_object_dot_notiation():

    class MyObject(object):
        pass

    output = MyObject()
    output.nested = MyObject()

    field = Field(source='nested.source', required=True)
    session = Session(field, {'name': 'mike'}, output)
    session.data = 'mike'

    update_output_to_source(session)
    assert output.nested.source == 'mike'


def test_update_output_to_source_with_dict():

    data = {
        'source': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    output = {}

    field = Field(source='source', required=True)
    session = Session(field, data, output)
    session.data = data['source']
    update_output_to_source(session)
    assert output == {'source': 'mike'}


def test_update_output_to_source_invalid_output_type():

    data = {
        'source': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    output = 1
    field = Field(source='source', required=True)
    session = Session(field, data, output)
    with pytest.raises(FieldError):
        update_output_to_source(session)
