import pytest

from kim.field import Field, FieldInvalid, FieldError
from kim.pipelines.base import get_data_from_source, update_output


def test_get_data_from_source_pipe():

    data = {
        'name': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    default = 'bar'
    field = Field(name='foo', required=True)
    field2 = Field(name='foo', default=default, required=False)
    field3 = Field(name='foo', allow_none=False, required=False)

    with pytest.raises(FieldInvalid):
        get_data_from_source(field, data)

    assert get_data_from_source(field2, data) == default

    with pytest.raises(FieldInvalid):
        get_data_from_source(field3, data)


def test_update_output_with_object():

    data = {
        'name': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    class MyObject(object):
        pass

    output = MyObject()
    field = Field(name='name', required=True)
    update_output(field, data['name'], output)
    assert output.name == 'mike'


def test_update_output_with_dict():

    data = {
        'name': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    output = {}

    field = Field(name='name', required=True)
    update_output(field, data['name'], output)
    assert output == {'name': 'mike'}


def test_update_output_invalid_output_type():

    data = {
        'name': 'mike',
        'test': 'true',
        'nested': {'foo': 'bar'}
    }

    field = Field(name='name', required=True)
    with pytest.raises(FieldError):
        update_output(field, data['name'], 1)
