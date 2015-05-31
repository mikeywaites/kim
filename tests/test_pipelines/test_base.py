import pytest

from kim.field import Field, FieldError
from kim.pipelines.base import get_data_from_source


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

    with pytest.raises(FieldError):
        get_data_from_source(field, data)

    assert get_data_from_source(field2, data) == default

    with pytest.raises(FieldError):
        get_data_from_source(field3, data)
