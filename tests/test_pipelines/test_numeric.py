import pytest

from kim.field import FieldInvalid, Integer
from kim.pipelines.base import Session
from kim.pipelines.numeric import is_valid_integer

from ..conftest import get_mapper_session


def test_is_valid_integer_pipe():
    """test piping data through is_valid_integer.
    """

    field = Integer(name='test')
    session = Session(field, 'test', {})

    with pytest.raises(FieldInvalid):
        is_valid_integer(session)

    session.data = '2'
    assert is_valid_integer(session) == 2
    session.data = 2
    assert is_valid_integer(session) == 2
    session.data = 2.3
    assert is_valid_integer(session) == 2


def test_integer_input():

    field = Integer(name='name', required=True)

    mapper_session = get_mapper_session(
        data={'email': 'mike@mike.com'}, output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    mapper_session = get_mapper_session(
        data={'name': 'foo', 'email': 'mike@mike.com'}, output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    output = {}
    mapper_session = get_mapper_session(
        data={'name': 2, 'email': 'mike@mike.com'}, output=output)
    field.marshal(mapper_session)
    assert output == {'name': 2}


def test_integer_field_invalid_type():

    field = Integer(name='name')
    mapper_session = get_mapper_session(
        data={'name': None, 'email': 'mike@mike.com'}, output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)


def test_integer_output():

    class Foo(object):
        name = 2

    field = Integer(name='name', required=True)

    output = {}
    mapper_session = get_mapper_session(obj=Foo(), output=output)
    field.serialize(mapper_session)
    assert output == {'name': 2}


def test_marshal_read_only_integer():

    field = Integer(name='name', read_only=True, required=True)

    output = {}
    mapper_session = get_mapper_session(
        data={'id': 2, 'email': 'mike@mike.com'}, output=output)

    field.marshal(mapper_session)
    assert output == {}


def test_is_valid_choice():

    field = Integer(name='type', choices=[1, 2])
    output = {}
    mapper_session = get_mapper_session(data={'type': 3}, output=output)
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    mapper_session = get_mapper_session(data={'type': 1}, output=output)
    field.marshal(mapper_session)
    assert output == {'type': 1}
