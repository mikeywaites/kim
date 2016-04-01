from datetime import datetime, date
from iso8601.iso8601 import Utc

import pytest

from kim.field import FieldInvalid, DateTime, Date
from kim.pipelines.base import Session
from kim.pipelines.datetime import is_valid_datetime

from ..conftest import get_mapper_session


def test_is_valid_datetime_pipe():
    """test piping data through is_valid_datetime.
    """

    field = DateTime(name='test')
    session = Session(field, 'test', {})

    with pytest.raises(FieldInvalid):
        is_valid_datetime(session)

    session.data = '2016-02-29T12:00:12Z'
    assert is_valid_datetime(session) == \
        datetime(2016, 2, 29, 12, 0, 12, tzinfo=Utc())
    session.data = '2015-06-29T08:00:12Z'
    assert is_valid_datetime(session) == \
        datetime(2015, 6, 29, 8, 0, 12, tzinfo=Utc())


def test_datetime_input():

    field = DateTime(name='date', required=True)

    mapper_session = get_mapper_session(
        data={'email': 'mike@mike.com'}, output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    mapper_session = get_mapper_session(
        data={'date': 'bla', 'email': 'mike@mike.com'},
        output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    output = {}
    mapper_session = get_mapper_session(
        data={'date': '2015-06-29T08:00:12Z', 'email': 'mike@mike.com'},
        output=output)
    field.marshal(mapper_session)
    assert output == {'date': datetime(2015, 6, 29, 8, 0, 12, tzinfo=Utc())}


def test_datetime_field_invalid_type():

    field = DateTime(name='date')
    mapper_session = get_mapper_session(
        data={'date': None, 'email': 'mike@mike.com'}, output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)


def test_datetime_output():

    class Foo(object):
        date = datetime(2015, 6, 29, 8, 0, 12, tzinfo=Utc())

    field = DateTime(name='date', required=True)

    output = {}
    mapper_session = get_mapper_session(obj=Foo(), output=output)
    field.serialize(mapper_session)
    assert output == {'date': '2015-06-29T08:00:12+00:00'}


def test_marshal_read_only_datetime():

    field = DateTime(name='date', read_only=True, required=True)

    output = {}
    mapper_session = get_mapper_session(
        data={'date': '2015-06-29T08:00:12Z', 'email': 'mike@mike.com'},
        output=output)

    field.marshal(mapper_session)
    assert output == {}


def test_date_input():

    field = Date(name='date', required=True)

    mapper_session = get_mapper_session(
        data={'email': 'mike@mike.com'}, output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    mapper_session = get_mapper_session(
        data={'date': 'bla', 'email': 'mike@mike.com'},
        output={})
    with pytest.raises(FieldInvalid):
        field.marshal(mapper_session)

    output = {}
    mapper_session = get_mapper_session(
        data={'date': '2015-06-29', 'email': 'mike@mike.com'},
        output=output)
    field.marshal(mapper_session)
    assert output == {'date': date(2015, 6, 29)}


def test_date_output():

    class Foo(object):
        date = date(2015, 6, 29)

    field = Date(name='date', required=True)

    output = {}
    mapper_session = get_mapper_session(obj=Foo(), output=output)
    field.serialize(mapper_session)
    assert output == {'date': '2015-06-29'}
