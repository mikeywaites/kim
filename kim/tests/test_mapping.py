#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim import types
from kim.exceptions import ValidationError
from kim.mapping import Mapping, mapping_iterator


class NotAType(object):

    def __init__(self, *args, **kwargs):
        pass


class MappingTest(unittest.TestCase):

    def test_setting_mapping_fields(self):

        name = types.TypeMapper('name', types.String())
        not_a = NotAType('foo')
        mapping = Mapping(name, not_a)
        self.assertIn(name, mapping.fields)
        self.assertNotIn(not_a, mapping.fields)

    def test_set_custom_mapping_colleciton(self):

        mapping = Mapping(collection=set())
        self.assertIsInstance(mapping.fields, set)

    def test_mapping_add_field(self):

        mapping = Mapping()
        name = types.TypeMapper('name', types.String())

        mapping.add_field(name)
        self.assertIn(name, mapping.fields)

    def test_iterate_over_mapping(self):

        name = types.TypeMapper('name', types.String())
        email = types.TypeMapper('email', types.String())
        mapping = Mapping(name, email)

        fields = [field for field in mapping]
        self.assertEqual(fields[0], name)
        self.assertEqual(fields[1], email)


class MappingIteratorTests(unittest.TestCase):

    def setUp(self):

        name = types.TypeMapper('name', types.String())
        id = types.TypeMapper('id', types.Integer())
        self.name = name
        self.id = id
        self.mapping = Mapping(name, id)

    def test_iterator_with_invalid_data(self):

        class Data(object):
            name = 'foo'
            id = 'bar'

        with self.assertRaises(ValidationError):
            [(f, v) for f, v in mapping_iterator(self.mapping, Data())]

    def test_field_appears_in_errors_when_invalid(self):

        class Data(object):
            name = 'foo'
            id = 'bar'

        try:
            [(f, v) for f, v in mapping_iterator(self.mapping, Data())]
        except ValidationError as e:
            self.assertIn('id', e.message)

    def test_field_value_yielded_when_valid(self):

        class Data(object):
            name = 'foo'
            id = 1

        exp = [(self.name, 'foo'), (self.id, 1)]
        result = [(f, v) for f, v in mapping_iterator(self.mapping, Data())]

        self.assertEqual(exp, result)

    def test_field_value_yielded_from_dict_when_valid(self):

        data = {'name': 'foo', 'id': 1}

        exp = [(self.name, 'foo'), (self.id, 1)]
        result = [(f, v) for f, v in mapping_iterator(self.mapping, data)]

        self.assertEqual(exp, result)

    def test_non_required_mapped_type_uses_default_value(self):

        name = types.TypeMapper('name', types.String(),
                                required=False, default='baz')
        mapping = Mapping(name)
        result = [(f, v) for f, v in mapping_iterator(mapping, {})]
        exp = [(name, 'baz')]

        self.assertEqual(result, exp)
