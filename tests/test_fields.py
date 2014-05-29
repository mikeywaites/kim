#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.fields import Field


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

    def test_srt_field_id_param(self):
        """ensure that field_id is correctly set when passed as a kwarg
        """
        field = Field('name', MyType(), field_id='other_name')
        self.assertEqual(field.field_id, 'other_name')
        self.assertEqual(field._field_id, 'other_name')
