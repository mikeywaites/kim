import pytest

from kim.field import (
    Field,
    FieldError,
    FieldInvalid,
    FieldOptsError,
    FieldOpts,
    DEFAULT_ERROR_MSGS,
)

from kim.pipelines.marshaling import MarshalPipeline
from kim.pipelines.serialization import SerializePipeline


def test_field_opts_correctly_set_for_field():

    new_field = Field(
        required=True, default="bar", source="new_field", name="other_field"
    )

    assert new_field.opts.required is True
    assert new_field.opts.default == "bar"
    assert new_field.opts.source == "new_field"
    assert new_field.opts.name == "other_field"


def test_field_extra_marshal_pipes_set():

    foo = lambda x: "foo"

    new_field = Field(
        required=True,
        default="bar",
        source="new_field",
        name="other_field",
        extra_marshal_pipes={"output": [foo]},
    )

    assert new_field.opts.extra_marshal_pipes == {"output": [foo]}


def test_field_extra_serialize_pipes_set():

    foo = lambda x: "foo"

    new_field = Field(
        required=True,
        default="bar",
        source="new_field",
        name="other_field",
        extra_serialize_pipes={"output": [foo]},
    )

    assert new_field.opts.extra_serialize_pipes == {"output": [foo]}


def test_field_name_defaults_to_attribute_name():
    new_field = Field(required=True, default="bar", attribute_name="other_field")

    assert new_field.opts.attribute_name == "other_field"
    assert new_field.opts.name == "other_field"


def test_field_source_defaults_to_name():
    new_field = Field(required=True, default="bar", name="other_field")

    assert new_field.opts.source == "other_field"
    assert new_field.opts.name == "other_field"


def test_get_field_name():
    invalid_field = Field(required=True, default="bar")

    name_field = Field(required=True, default="bar", name="other_field")

    attr_field = Field(required=True, default="bar", attribute_name="other_field")

    with pytest.raises(FieldError):
        assert invalid_field.name

    assert name_field.name == "other_field"
    assert attr_field.name == "other_field"


def test_field_invalid():

    field = Field(name="foo")

    with pytest.raises(FieldInvalid):

        field.invalid(error_type="type_error")


def test_field_custom_error_messages_updates_defaults():

    msgs = {"type_error": "This field failed to validate due to a type error"}
    field = Field(name="foo", error_msgs=msgs)
    exp = DEFAULT_ERROR_MSGS.copy()
    exp.update(msgs)
    assert field.opts.error_msgs == exp


def test_field_invalid_custom_error_messages():

    msgs = {"type_error": "This field failed to validate due to a type error"}
    field = Field(name="foo", error_msgs=msgs)

    try:
        field.invalid(error_type="type_error")
    except FieldInvalid as e:
        assert e.message == msgs["type_error"]


def test_get_field_input_pipe():

    field = Field(name="foo")

    assert field.marshal_pipeline == MarshalPipeline


def test_get_field_output_pipe():

    field = Field(name="foo")

    assert field.serialize_pipeline == SerializePipeline


def test_field_invalid_opts_class():
    class CustomOpts(FieldOpts):
        def validate(self, *args, **kwargs):

            raise FieldOptsError("sorry this is invalid")

    class PhoneNumber(Field):

        opts_class = CustomOpts

    with pytest.raises(FieldError):

        PhoneNumber()
