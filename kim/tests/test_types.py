#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.roles import Role
from kim.types import Nested, TypeABC, String
from kim.mapping import Mapping


class TypeABCTests(unittest.TestCase):

    def test_type_name_correctly_set(self):

        my_type = TypeABC('email')
        self.assertEqual(my_type.name, 'email')

    def test_source_set_from_type_name_when_not_specified(self):

        my_type = TypeABC('email')
        self.assertEqual(my_type.source, 'email')

    def test_set_custom_source_param(self):

        my_type = TypeABC('email', source='email_address')
        self.assertEqual(my_type.source, 'email_address')

    def test_get_value(self):

        my_type = TypeABC('email', source='email_address')
        self.assertEqual(my_type.get_value('foo'), 'foo')


class NestedTypeTests(unittest.TestCase):

    def test_nested_requires_valid_mapping_type(self):

        with self.assertRaises(TypeError):
            Nested('users', mapped=list())

    def test_nested_type_sets_role(self):

        role = Role('foo')
        mapping = Mapping('users')
        nested = Nested('name', mapped=mapping, role=role)
        self.assertEqual(nested.role, role)

    def test_nested_type_with_core_mapping_type(self):

        mapping = Mapping('users')
        nested = Nested('name', mapped=mapping)
        self.assertEqual(nested.mapping, mapping)

    def test_set_new_mapping_on_nested_type(self):

        mapping = Mapping('users')
        new_mapping = Mapping('people')

        nested = Nested('name', mapped=mapping)
        nested.mapping = new_mapping
        self.assertEqual(nested.mapping, new_mapping)

    def test_get_mapping_with_no_role(self):

        mapping = Mapping('users')
        nested = Nested('name', mapped=mapping)
        self.assertEqual(nested.get_mapping(), mapping)

    def test_get_mapping_with_role_set(self):

        name, email = String('email'), String('name')

        role = Role('foo', 'name')
        mapping = Mapping('users', name, email)
        nested = Nested('name', mapped=mapping, role=role)

        mapped = nested.get_mapping()
        self.assertNotEqual(mapped, mapping)

    def test_get_value(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name, email = String('email'), String('name')
        mapping = Mapping('users', name, email)

        nested = Nested('user', mapped=mapping)
        output = nested.get_value(Inner())
        exp = {
            'name': 'foo',
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)
