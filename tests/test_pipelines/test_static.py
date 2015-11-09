import pytest

from kim.field import FieldInvalid, Static
from kim.pipelines.base import Session
from kim.pipelines.static import get_static_value


def test_get_static_value():

    field = Static('foo', name='test')
    session = Session(field, 'bar', {})

    assert get_static_value(session) == 'foo'


def test_static_read_only():

    field = Static('foo', name='test')
    assert field.opts.read_only

    field = Static('foo', read_only=False, name='test')
    assert field.opts.read_only


def test_static_output():

    class Foo(object):
        name = 'value'

    field = Static('foo', name='name', required=True)

    output = {}
    field.serialize(Foo(), output)
    assert output == {'name': 'foo'}
