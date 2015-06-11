import pytest

from kim.field import FieldError, Integer
from kim.pipelines.numeric import is_valid_integer


def test_is_valid_integer_pipe():
    """test piping data through is_valid_integer.
    """

    field = Integer()

    with pytest.raises(FieldError):
        is_valid_integer(field, 'foo')

    assert is_valid_integer(field, '2') == 2
    assert is_valid_integer(field, 2) == 2
    assert is_valid_integer(field, 2.3) == 2


def test_integer_input():

    field = Integer(name='name', required=True)

    with pytest.raises(FieldError):
        field.marshal({'email': 'mike@mike.com'})

    with pytest.raises(FieldError):
        field.marshal({'name': 'foo', 'email': 'mike@mike.com'})

    result = field.marshal({'name': 2, 'email': 'mike@mike.com'})
    assert result == 2


def test_integer_output():

    class Foo(object):
        name = 'value'

    field = Integer(name='name', required=True)
    result = field.serialize(Foo())
    assert result == 'value'
