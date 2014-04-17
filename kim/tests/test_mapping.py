#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import mock

from kim import types
from kim.exceptions import MappingErrors
from kim.mapping import Mapping, marshal, serialize, MappingIterator
from kim.type_mapper import TypeMapper


class NotAType(object):

    def __init__(self, *args, **kwargs):
        pass


class MappingTest(unittest.TestCase):

    def test_setting_mapping_fields(self):

        name = TypeMapper('name', types.String())
        not_a = NotAType('foo')
        mapping = Mapping(name, not_a)
        self.assertIn(name, mapping.fields)
        self.assertNotIn(not_a, mapping.fields)

    def test_set_custom_mapping_colleciton(self):

        mapping = Mapping(collection=set())
        self.assertIsInstance(mapping.fields, set)

    def test_mapping_add_field(self):

        mapping = Mapping()
        name = TypeMapper('name', types.String())

        mapping.add_field(name)
        self.assertIn(name, mapping.fields)

    def test_iterate_over_mapping(self):

        name = TypeMapper('name', types.String())
        email = TypeMapper('email', types.String())
        mapping = Mapping(name, email)

        fields = [field for field in mapping]
        self.assertEqual(fields[0], name)
        self.assertEqual(fields[1], email)


class MappingIteratorTest(unittest.TestCase):
    def test_process_field_not_implemented(self):
        mi = MappingIterator()
        with self.assertRaises(NotImplementedError):
            mi.process_field(None, None)

    def test_update_output_not_implemented(self):
        mi = MappingIterator()
        with self.assertRaises(NotImplementedError):
            mi.update_output(None, None)

class MarshalTests(unittest.TestCase):

    def setUp(self):

        name = TypeMapper('name', types.String())
        id = TypeMapper('id', types.Integer())
        self.name = name
        self.id = id
        self.mapping = Mapping(name, id)

    def test_marshal_with_invalid_data(self):

        class Data(object):
            name = 'foo'
            id = 'bar'

        with self.assertRaises(MappingErrors):
            marshal(self.mapping, Data())

    def test_field_appears_in_errors_when_invalid(self):

        class Data(object):
            name = 'foo'
            id = 'bar'

        try:
            marshal(self.mapping, Data())
        except MappingErrors as e:
            self.assertIn('id', e.message)

    def test_field_values_returned_when_valid(self):

        class Data(object):
            name = 'foo'
            id = 1

        exp = {'name': 'foo', 'id': 1}
        result = marshal(self.mapping, Data())

        self.assertEqual(exp, result)

    def test_field_values_returned_from_dict_when_valid(self):

        data = {'name': 'foo', 'id': 1}

        result = marshal(self.mapping, data)

        self.assertEqual(data, result)

    def test_non_required_mapped_type_uses_default_value(self):

        name = TypeMapper('name', types.String(required=False),
                                default='baz')
        mapping = Mapping(name)
        result = marshal(mapping, {})
        exp = {'name': 'baz'}

        self.assertEqual(result, exp)

    def test_default_not_used_when_falsey(self):

        name = TypeMapper('order', types.Integer(required=False),
                                default=123)
        mapping = Mapping(name)
        result = marshal(mapping, {'order': 0})
        exp = {'order': 0}

        self.assertEqual(result, exp)

    def test_type_not_called_when_none(self):
        mockedtype = mock.MagicMock(default=None)

        name = TypeMapper('name', mockedtype)
        mapping = Mapping(name)
        marshal(mapping, {})

        self.assertFalse(mockedtype.marshal_value.called)

    def test_type_not_called_when_not_none(self):
        mockedtype = mock.MagicMock(default=None)

        name = TypeMapper('name', mockedtype)
        mapping = Mapping(name)
        marshal(mapping, {'name': 'bob'})

        self.assertTrue(mockedtype.marshal_value.called)

    def test_field_value_returned_when_different_source(self):
        name = TypeMapper('name', types.String(), source='different_name')
        id = TypeMapper('id', types.Integer())
        mapping = Mapping(name, id)

        data = {'name': 'bar', 'id': 1}

        exp = {'different_name': 'bar', 'id': 1}
        result = marshal(mapping, data)

        self.assertEqual(exp, result)

    def test_many(self):

        data = [{'name': 'foo', 'id': 1}, {'name': 'bar', 'id': 2}]

        result = marshal(self.mapping, data, many=True)

        self.assertEqual(data, result)

    def test_include_in_marshal(self):
        class NotIncludedType(types.Integer):
            def include_in_marshal(self):
                return False

        name = TypeMapper('name', types.String())
        id = TypeMapper('id', NotIncludedType())
        mapping = Mapping(name, id)

        data = {'name': 'bar', 'id': 1}

        result = marshal(mapping, data)

        exp = {'name': 'bar'}

        self.assertEqual(exp, result)




class SerializeTests(unittest.TestCase):

    def setUp(self):

        name = TypeMapper('name', types.String())
        id = TypeMapper('id', types.Integer())
        self.name = name
        self.id = id
        self.mapping = Mapping(name, id)

    def test_serialize_with_invalid_data(self):

        class Data(object):
            name = 'foo'
            id = 'bar'

        with self.assertRaises(MappingErrors):
            serialize(self.mapping, Data())

    def test_field_appears_in_errors_when_invalid(self):

        class Data(object):
            name = 'foo'
            id = 'bar'

        try:
            serialize(self.mapping, Data())
        except MappingErrors as e:
            self.assertIn('id', e.message)

    def test_field_values_returned_when_valid(self):

        class Data(object):
            name = 'foo'
            id = 1

        exp = {'name': 'foo', 'id': 1}
        result = serialize(self.mapping, Data())

        self.assertEqual(exp, result)

    def test_field_values_returned_from_dict_when_valid(self):

        data = {'name': 'foo', 'id': 1}

        result = serialize(self.mapping, data)

        self.assertEqual(data, result)

    def test_non_required_mapped_type_uses_default_value(self):

        name = TypeMapper('name', types.String(required=False),
                          default='baz')
        mapping = Mapping(name)
        result = serialize(mapping, {})
        exp = {'name': 'baz'}

        self.assertEqual(result, exp)

    def test_field_value_returned_when_different_source(self):
        name = TypeMapper('name', types.String(), source='different_name')
        id = TypeMapper('id', types.Integer())
        mapping = Mapping(name, id)

        data = {'different_name': 'bar', 'id': 1}

        exp = {'name': 'bar', 'id': 1}
        result = serialize(mapping, data)

        self.assertEqual(exp, result)

    def test_many(self):

        data = [{'name': 'foo', 'id': 1}, {'name': 'bar', 'id': 2}]

        result = serialize(self.mapping, data, many=True)

        self.assertEqual(data, result)

    def test_many_with_errors(self):

        data = [{'name': 'foo', 'id': 'abc'}, {'name': 'baz', 'id': 5}, {'name': 'bar', 'id': 'abc'}]

        self.assertRaises(MappingErrors, lambda: serialize(self.mapping, data, many=True))

        try:
            serialize(self.mapping, data, many=True)
        except MappingErrors as e:
            exp = [
                {'id': [u'This field was of an incorrect type']},
                {},
                {'id': [u'This field was of an incorrect type']}
            ]
            self.assertEqual(exp, e.message)

    def test_include_in_serialize(self):
        class NotIncludedType(types.Integer):
            def include_in_serialize(self):
                return False

        name = TypeMapper('name', types.String())
        id = TypeMapper('id', NotIncludedType())
        mapping = Mapping(name, id)

        data = {'name': 'bar', 'id': 1}

        result = serialize(mapping, data)

        exp = {'name': 'bar'}

        self.assertEqual(exp, result)

    def test_type_not_called_when_none(self):
        mockedtype = mock.MagicMock(default=None)

        name = TypeMapper('name', mockedtype)
        mapping = Mapping(name)
        serialize(mapping, {})

        self.assertFalse(mockedtype.serialize_value.called)

    def test_type_not_called_when_not_none(self):
        mockedtype = mock.MagicMock(default=None)

        name = TypeMapper('name', mockedtype)
        mapping = Mapping(name)
        serialize(mapping, {'name': 'bob'})

        self.assertTrue(mockedtype.serialize_value.called)

