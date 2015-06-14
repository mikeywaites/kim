import pytest

from kim.field import Field, FieldError, FieldInvalid, Input, Output


def test_field_opts_correctly_set_for_field():

    new_field = Field(
        required=True,
        default='bar',
        source='new_field',
        name='other_field')

    assert new_field.opts.required is True
    assert new_field.opts.default == 'bar'
    assert new_field.opts.source == 'new_field'
    assert new_field.opts.name == 'other_field'


def test_field_name_defaults_to_attribute_name():
    new_field = Field(
        required=True,
        default='bar',
        attribute_name='other_field')

    assert new_field.opts.attribute_name == 'other_field'
    assert new_field.opts.name == 'other_field'


def test_field_source_defaults_to_name():
    new_field = Field(
        required=True,
        default='bar',
        name='other_field')

    assert new_field.opts.source == 'other_field'
    assert new_field.opts.name == 'other_field'


def test_get_field_name():
    invalid_field = Field(
        required=True,
        default='bar')

    name_field = Field(
        required=True,
        default='bar',
        name='other_field')

    attr_field = Field(
        required=True,
        default='bar',
        attribute_name='other_field')

    with pytest.raises(FieldError):
        assert invalid_field.name

    assert name_field.name == 'other_field'
    assert attr_field.name == 'other_field'


def test_field_invalid():

    field = Field(name='foo')

    with pytest.raises(FieldInvalid):

        field.invalid('not valid')


def test_get_field_input_pipe():

    field = Field(name='foo')

    assert field.input_pipe == Input


def test_get_field_output_pipe():

    field = Field(name='foo')

    assert field.output_pipe == Output
