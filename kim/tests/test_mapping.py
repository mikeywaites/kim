#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim import types
from kim.mapping import Mapping


class NotAType(object):

    def __init__(self, *args, **kwargs):
        pass


class MappingTest(unittest.TestCase):

    def test_name_arg_required_for_mapping(self):

        with self.assertRaises(TypeError):
            Mapping()

    def test_name_correctly_set_for_mapping(self):

        mapping = Mapping('users')
        self.assertEqual(mapping.name, 'users')

    def test_setting_mapping_fields(self):

        name = types.String('name')
        not_a = NotAType('foo')
        mapping = Mapping('users', name, not_a)
        self.assertIn(name, mapping.fields)
        self.assertNotIn(not_a, mapping.fields)

    def test_set_custom_mapping_colleciton(self):

        mapping = Mapping('users', collection=set())
        self.assertIsInstance(mapping.fields, set)

    def test_mapping_add_field(self):

        mapping = Mapping('users')
        name = types.String('name')

        mapping.add_field(name)
        self.assertIn(name, mapping.fields)

    def test_iterate_over_mapping(self):

        name = types.String('name')
        email = types.String('email')
        mapping = Mapping('users', name, email)

        fields = [field for field in mapping]
        self.assertEqual(fields[0], name)
        self.assertEqual(fields[1], email)
