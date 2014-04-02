#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.roles import Role
from kim.mapping import Mapping
from kim.exceptions import ValidationError
from kim.types import (Nested, String, TypeMapper,
                       CollectionTypeMapper, Integer,
                       BaseType, TypedType)


class BaseTypeTests(unittest.TestCase):

    def test_get_value(self):

        my_type = BaseType()
        self.assertEqual(my_type.get_value('foo'), 'foo')

    def test_from_value(self):

        my_type = BaseType()
        self.assertEqual(my_type.from_value('foo'), 'foo')

    def test_validate(self):

        my_type = BaseType()
        self.assertTrue(my_type.validate('foo'), True)


class TypedTypeTests(unittest.TestCase):

    def test_validate_allows_none(self):

        class MyType(TypedType):

            type_ = list

        my_type = MyType()
        self.assertTrue(my_type.validate(None))

    def test_validate_requires_valid_type_when_not_is_none(self):
        class MyType(TypedType):

            type_ = list

        my_type = MyType()
        with self.assertRaises(ValidationError):
            self.assertTrue(my_type.validate(''))

    def test_validate(self):

        class MyType(TypedType):

            type_ = list

        self.assertTrue(MyType().validate([]))


class StringTypeTests(unittest.TestCase):

    def test_validate_requires_valid_string_type(self):

        my_type = String()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_string_type(self):

        my_type = String()
        my_type.validate(u'foo')


class IntegerTypeTests(unittest.TestCase):

    def test_validate_requires_valid_string_type(self):

        my_type = Integer()
        with self.assertRaises(ValidationError):
            my_type.validate('')

    def test_validate_string_type(self):

        my_type = Integer()
        my_type.validate(1)


class TypeMapperTests(unittest.TestCase):

    def test_type_name_correctly_set(self):

        mapped_type = TypeMapper('email', String())
        self.assertEqual(mapped_type.name, 'email')

    def test_source_set_from_type_name_when_not_specified(self):

        mapped_type = TypeMapper('email', String())
        self.assertEqual(mapped_type.source, 'email')

    def test_set_custom_source_param(self):

        mapped_type = TypeMapper('email', String(), source='email_address')
        self.assertEqual(mapped_type.source, 'email_address')

    def test_get_value(self):

        mapped_type = TypeMapper('email', String(), source='email_address')
        self.assertEqual(mapped_type.get_value('foo'), 'foo')

    def test_from_value(self):

        mapped_type = TypeMapper('email', String(), source='email_address')
        self.assertEqual(mapped_type.from_value('foo'), 'foo')


class CollectionTypeMapperTests(unittest.TestCase):
    def test_get_value(self):
        mct = CollectionTypeMapper('l', Integer())
        self.assertEqual(mct.get_value([1, 2, 3]), [1, 2, 3])


class NestedTypeTests(unittest.TestCase):

    def test_nested_requires_valid_mapping_type(self):

        with self.assertRaises(TypeError):
            Nested(mapped=list())

    def test_nested_type_sets_role(self):

        role = Role('foo')
        mapping = Mapping('users')
        nested = Nested(mapped=mapping, role=role)
        self.assertEqual(nested.role, role)

    def test_nested_type_with_core_mapping_type(self):

        mapping = Mapping('users')
        nested = Nested(mapped=mapping)
        self.assertEqual(nested.mapping, mapping)

    def test_set_new_mapping_on_nested_type(self):

        mapping = Mapping('users')
        new_mapping = Mapping('people')

        nested = Nested(mapped=mapping)
        nested.mapping = new_mapping
        self.assertEqual(nested.mapping, new_mapping)

    def test_get_mapping_with_no_role(self):

        mapping = Mapping('users')
        nested = Nested(mapped=mapping)
        self.assertEqual(nested.get_mapping(), mapping)

    def test_get_mapping_with_role_set(self):

        name, email = TypeMapper('email', String()), TypeMapper('name', String())

        role = Role('foo', 'name')
        mapping = Mapping('users', name, email)
        nested = Nested(mapped=mapping, role=role)

        mapped = nested.get_mapping()
        self.assertNotEqual(mapped, mapping)

    def test_get_value(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name, email = TypeMapper('email', String()), TypeMapper('name', String())
        mapping = Mapping('users', name, email)

        nested = Nested(mapped=mapping)
        output = nested.get_value(Inner())
        exp = {
            'name': 'foo',
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)
