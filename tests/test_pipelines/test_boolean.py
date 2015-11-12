import pytest

from ..conftest import get_mapper_session
from kim.field import FieldInvalid, Boolean
from kim.pipelines.base import Session, is_valid_choice


def test_is_allowed_value():

    field = Boolean(name='test')
    session = Session(field, 'test', {})

    with pytest.raises(FieldInvalid):
        is_valid_choice(session)

    session.data = True
    assert is_valid_choice(session) is True

    session.data = 'true'
    assert is_valid_choice(session) == 'true'

    session.data = '1'
    assert is_valid_choice(session) == '1'

    session.data = 'True'
    assert is_valid_choice(session) == 'True'

    session.data = False
    assert is_valid_choice(session) is False

    session.data = 'false'
    assert is_valid_choice(session) == 'false'

    session.data = '0'
    assert is_valid_choice(session) == '0'

    session.data = 0
    assert is_valid_choice(session) == 0

    session.data = 'False'
    assert is_valid_choice(session) == 'False'


def test_is_allowed_value_with_custom_values():

    field = Boolean(name='test', true_boolean_values=['foo'],
                    false_boolean_values=['bar'])

    data = True
    session = Session(field, data, {})

    with pytest.raises(FieldInvalid):
        is_valid_choice(session)

    session.data = False
    with pytest.raises(FieldInvalid):
        is_valid_choice(session)

    session.data = 'foo'
    assert is_valid_choice(session) == 'foo'
    session.data = 'bar'
    assert is_valid_choice(session) == 'bar'


def test_boolean_input():

    field = Boolean(name='is_active', required=True)

    output = {}
    mapper_session = get_mapper_session(
        data={'is_active': False, 'email': 'mike@mike.com'}, output=output)

    field.marshal(mapper_session)
    assert output == {'is_active': False}

    mapper_session = get_mapper_session(
        data={'is_active': 'false', 'email': 'mike@mike.com'}, output=output)

    field.marshal(mapper_session)
    assert output == {'is_active': False}

    mapper_session = get_mapper_session(
        data={'is_active': True, 'email': 'mike@mike.com'}, output=output)

    field.marshal(mapper_session)
    assert output == {'is_active': True}

    mapper_session = get_mapper_session(
        data={'is_active': 'true', 'email': 'mike@mike.com'}, output=output)

    field.marshal(mapper_session)
    assert output == {'is_active': True}


def test_boolean_input_with_allow_none():

    field = Boolean(name='is_active', required=False, allow_none=True)

    output = {}
    mapper_session = get_mapper_session(
        data={'is_active': None, 'email': 'mike@mike.com'}, output=output)

    field.marshal(mapper_session)
    assert output == {'is_active': None}


def test_boolean_output():

    class Foo(object):
        is_active = True

    field = Boolean(name='is_active', required=True)

    output = {}
    mapper_session = get_mapper_session(obj=Foo(), output=output)
    field.serialize(mapper_session)
    assert output == {'is_active': True}
