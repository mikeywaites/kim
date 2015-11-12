# encoding: utf-8
import pytest

from ..conftest import marshal_mapper_session, serialize_mapper_session

from kim.field import FieldInvalid, String
from kim.pipelines.base import Session
from kim.pipelines.string import is_valid_string


def test_is_valid_string_pipe():
    """test piping data through is_valid_string.
    """

    class InvalidString(object):

        def __str__(self):
            raise ValueError('invalid string')

    field = String(name='test')
    invalid_string = InvalidString()
    session = Session(field, invalid_string, {})

    with pytest.raises(FieldInvalid):
        is_valid_string(session)

    session.data = 'yes'
    assert is_valid_string(session) == 'yes'


def test_string_input():
    # TODO this requires fleshing out some more..

    field = String(name='name', required=True)

    output = {}
    mapper_session = marshal_mapper_session(
        {'name': 'foo', 'email': 'mike@mike.com'}, output)

    field.marshal(mapper_session)
    assert output == {'name': 'foo'}


def test_string_output():
    # TODO this requires fleshing out some more..

    class Foo(object):
        name = 'value'

    field = String(name='name', required=True)

    output = {}
    mapper_session = serialize_mapper_session(Foo(), output)
    field.serialize(mapper_session)
    assert output == {'name': 'value'}


def test_string_input_unicode():
    # TODO this requires fleshing out some more..

    field = String(name='name', required=True)

    output = {}
    mapper_session = marshal_mapper_session({'name': u'unicöde'}, output)
    field.marshal(mapper_session)
    assert output == {'name': u'unicöde'}


def test_marshal_read_only_string():

    field = String(name='name', read_only=True, required=True)

    output = {}
    mapper_session = marshal_mapper_session(
        {'name': 'foo', 'email': 'mike@mike.com'}, output)
    field.marshal(mapper_session)
    assert output == {}


def test_is_valid_choice():

    field = String(name='type', choices=['one', 'two'])
    output = {}
    mapper_session = marshal_mapper_session({'type': 'three'}, output)
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    mapper_session = marshal_mapper_session({'type': 'one'}, output)
    field.marshal(mapper_session)
    assert output == {'type': 'one'}
