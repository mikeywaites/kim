#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import mock

from kim.fields import Field
from kim.types import String
from kim.exceptions import ValidationError


class MyType(object):

    _kim_type = True


class FieldTests(unittest.TestCase):

    def test_field_require_type_argument(self):
        """ensure that if no valid type argument is passed to ``Field``
        a TypeError is raised.
        """

        with self.assertRaises(TypeError):
            Field('name')

    def test_field_type_accepted_as_first_argument_to_field(self):
        """ensure that if a ``Type`` is passed as the first argument to
        ``Field`` as a class or an instance of ``Type``, ``Field.field_type``
        is correctly set.
        """

        field = Field(MyType())
        self.assertIsInstance(field.field_type, MyType)
        self.assertFalse(field.name)

        field = Field(MyType)
        self.assertIsInstance(field.field_type, MyType)
        self.assertFalse(field.name)

    def test_setting_field_type_as_kwarg(self):
        """ensure ``Field.field_type`` can be set using a kwarg passed to
        ``Field`` and accepts both ``Type`` classes and instances of ``Type``
        """
        field = Field(field_type=MyType())
        self.assertIsInstance(field.field_type, MyType)

        field = Field(field_type=MyType)
        self.assertIsInstance(field.field_type, MyType)

    def test_field_raises_error_if_field_type_arg_and_field_type_kwarg(self):
        """ensure and Exception is raised if ``Type`` is passed as an arg and
        as a kwarg
        """

        with self.assertRaises(Exception):
            Field(MyType, field_type=MyType())

    def test_set_field_name_from_first_arg(self):
        """ensure that the ``Field`` name can be set by passing a string
        as the first argument to the field constructor
        """

        field = Field('name', MyType())
        self.assertEqual(field.name, 'name')

    def test_set_source_param(self):
        """ensure that source is correctly set when passed as a kwarg
        """
        field = Field('name', MyType(), source='other_name')
        self.assertEqual(field.source, 'other_name')
        self.assertEqual(field._source, 'other_name')

    def test_source_returns_name_when_not_set(self):
        """ensure that when no source param is passed to ``Field`` the name
        value is returned
        """
        field = Field('name', MyType())
        self.assertEqual(field.source, 'name')
        self.assertEqual(field._source, None)

    def test_set_field_id_param(self):
        """ensure that field_id is correctly set when passed as a kwarg
        """
        field = Field('name', MyType(), field_id='other_name')
        self.assertEqual(field.field_id, 'other_name')
        self.assertEqual(field._field_id, 'other_name')

    def test_field_id_returns_name_when_not_set(self):
        """ensure that field_id returns ``Field.name`` when ``Field._field_id``
        is None
        """
        field = Field('name', MyType())
        self.assertEqual(field.field_id, 'name')
        self.assertEqual(field._field_id, None)

    def test_read_only_field_is_valid_when_required_value_is_none(self):
        """ensure a read only field is always considered valid
        """
        field = Field('name', String(), required=True, read_only=True)
        self.assertTrue(field.is_valid(None))

    def test_required_field_raises_error_when_value_is_none(self):

        field = Field('name', String())
        with self.assertRaises(ValidationError):
            field.is_valid(None)

    def test_required_validation_error_message(self):

        field = Field('name', String())
        error = None
        try:
            field.is_valid(None)
        except ValidationError as e:
            error = e.message
        self.assertEqual(error, 'This is a required field')

    def test_non_required_field_and_allow_none(self):
        """ensure that a non required field that does not allow null values
        raises an error when validating None
        """

        field = Field('name', String(), required=False, allow_none=False)
        with self.assertRaises(ValidationError):
            field.is_valid(None)

    def test_field_allow_none_error_message(self):
        field = Field('name', String(), required=False, allow_none=False)
        error = None
        try:
            field.is_valid(None)
        except ValidationError as e:
            error = e.message
        self.assertEqual(error, 'This field can not be None')

    def test_field_type_validate_method_called(self):
        """ensure that after a field has run validation against required etc,
        it calls the validate method of the provided field type
        """
        mocked = mock.MagicMock()

        class MyValidateType(String):

            def validate(self, value):
                mocked()
                return super(MyValidateType, self).validate(value)

        field = Field('name', MyValidateType())
        field.is_valid('string')
        self.assertTrue(mocked.called)

    def test_extra_validators_run(self):

        mock_validator_1 = mock.MagicMock()
        mock_validator_2 = mock.MagicMock()
        mock_validator_3 = mock.MagicMock()
        validators = [mock_validator_1, mock_validator_2, mock_validator_3]

        field = Field('name', String(), extra_validators=validators)
        field.is_valid('string')
        self.assertTrue(mock_validator_1.called)
        self.assertTrue(mock_validator_2.called)
        self.assertTrue(mock_validator_3.called)
