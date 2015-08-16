import pytest

from kim.field import FieldInvalid, Integer
from kim.pipelines.numeric import is_valid_integer


def test_is_valid_integer_pipe():
    """test piping data through is_valid_integer.
    """

    field = Integer()

    with pytest.raises(FieldInvalid):
        is_valid_integer(field, 'foo')

    assert is_valid_integer(field, '2') == 2
    assert is_valid_integer(field, 2) == 2
    assert is_valid_integer(field, 2.3) == 2


def test_integer_input():

    field = Integer(name='name', required=True)

    with pytest.raises(FieldInvalid):
        field.marshal({'email': 'mike@mike.com'}, {})

    with pytest.raises(FieldInvalid):
        field.marshal({'name': 'foo', 'email': 'mike@mike.com'}, {})

    output = {}
    field.marshal({'name': 2, 'email': 'mike@mike.com'}, output)
    assert output == {'name': 2}


def test_integer_field_invalid_type():

    field = Integer(name='name')
    with pytest.raises(FieldInvalid):
        field.marshal({'name': None, 'email': 'mike@mike.com'}, {})


def test_integer_output():

    class Foo(object):
        name = 2

    field = Integer(name='name', required=True)

    output = {}
    field.serialize(Foo(), output)
    assert output == {'name': 2}


def test_marshal_read_only_integer():

    field = Integer(name='name', read_only=True, required=True)

    output = {}
    field.marshal({'id': 2, 'email': 'mike@mike.com'}, output)
    assert output == {}
