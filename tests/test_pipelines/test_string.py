import pytest

from kim.field import FieldError, String
from kim.pipelines.string import is_valid_string


def test_is_valid_string_pipe():
    """test piping data through is_valid_string.
    """

    class InvalidString(object):

        def __str__(self):
            raise ValueError('invalid string')

    field = String()
    invalid_string = InvalidString()

    with pytest.raises(FieldError):
        is_valid_string(field, invalid_string)

    assert is_valid_string(field, 'yes') == 'yes'


def test_string_input():
    # TODO this requires fleshing out some more..

    field = String(name='name', required=True)
    result = field.marshal({'name': 'foo', 'email': 'mike@mike.com'})
    assert result == 'foo'


def test_string_output():
    # TODO this requires fleshing out some more..

    class Foo(object):
        name = 'value'

    field = String(name='name', required=True)
    result = field.serialize(Foo())
    assert result == 'value'
