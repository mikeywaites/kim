#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re
import decimal
from datetime import date, datetime
from iso8601.iso8601 import Utc
import mock

from kim.roles import Role
from kim.mapping import Mapping
from kim.exceptions import ValidationError
from kim.types import (Nested, String, Collection, Integer, BaseType,
    TypedType, Date, DateTime, Regexp, Email, Float, Decimal, PositiveInteger)
from kim.type_mapper import TypeMapper


ImportByStringMapping = Mapping()


class BaseTypeTests(unittest.TestCase):

    def test_marshal_value(self):

        my_type = BaseType()
        self.assertEqual(my_type.marshal_value('foo'), 'foo')

    def test_serialize_value(self):

        my_type = BaseType()
        self.assertEqual(my_type.serialize_value('foo'), 'foo')

    def test_validate(self):

        my_type = BaseType()
        self.assertTrue(my_type.validate('foo'), True)


    def test_validate_raises_error_when_required_and_value_null(self):

        my_type = String(required=True)
        with self.assertRaises(ValidationError):
            my_type.validate(None)

    def test_validate_not_allow_none(self):
        my_type = String(allow_none=False, required=False)

        with self.assertRaises(ValidationError):
            my_type.validate(None)

    def test_validate_required_value_falsey(self):

        my_type = Integer(required=True)
        self.assertTrue(my_type.validate(0))

    def test_validate_allow_none(self):

        my_type = String(required=False, allow_none=True)

        self.assertTrue(my_type.validate(None))

    def test_validate_mapped_type(self):
        my_type = String(required=True, allow_none=False)

        self.assertTrue(my_type.validate('foo'))

    def test_set_allow_none(self):
        my_type = String(allow_none=False)
        self.assertEqual(my_type.allow_none, False)

    def test_include_in_serialize(self):
        my_type = String()
        self.assertTrue(my_type.include_in_serialize())

    def test_include_in_marshal_not_read_only(self):
        my_type = String(read_only=False)
        self.assertTrue(my_type.include_in_marshal())

    def test_include_in_marshal_read_only(self):
        my_type = String(read_only=True)
        self.assertFalse(my_type.include_in_marshal())

    def test_validate_read_only_not_none(self):
        my_type = String(read_only=True)
        with self.assertRaises(ValidationError):
            self.assertFalse(my_type.validate('bla'))

    def test_validate_read_only_none(self):
        my_type = String(read_only=True)
        self.assertTrue(my_type.validate(None))

    def test_validate_not_read_only(self):
        my_type = String(read_only=False)
        self.assertTrue(my_type.validate('bla'))


class TypedTypeTests(unittest.TestCase):

    def test_validate_requires_valid(self):
        class MyType(TypedType):

            type_ = list

        my_type = MyType()
        with self.assertRaises(ValidationError):
            self.assertTrue(my_type.validate(''))

    def test_validate(self):

        class MyType(TypedType):

            type_ = list

        self.assertTrue(MyType().validate([1]))

    def test_validate_requires_valid_choice(self):
        class MyType(TypedType):

            type_ = str

        my_type = MyType(choices=['choice1', 'choice2'])
        with self.assertRaises(ValidationError):
            my_type.validate('choice3')

    def test_validate_choice(self):
        class MyType(TypedType):

            type_ = str

        my_type = MyType(choices=['choice1', 'choice2'])
        self.assertTrue(my_type.validate('choice2'))


class StringTypeTests(unittest.TestCase):

    def test_validate_requires_valid_string_type(self):

        my_type = String()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_string_type(self):

        my_type = String()
        my_type.validate(u'foo')


class IntegerTypeTests(unittest.TestCase):

    def test_validate_requires_valid_integer_type(self):

        my_type = Integer()
        with self.assertRaises(ValidationError):
            my_type.validate('')

    def test_validate_integer_type(self):

        my_type = Integer()
        my_type.validate(1)


class PositiveIntegerTypeTests(unittest.TestCase):

    def test_validate_requires_valid_positive_integer_type(self):

        my_type = PositiveInteger()
        with self.assertRaises(ValidationError):
            my_type.validate(-6)

    def test_validate_positive_integer_type(self):

        my_type = PositiveInteger()
        my_type.validate(1)


class CollectionTypeTests(unittest.TestCase):

    def test_marshal_value(self):

        c = Collection(Integer())
        self.assertEqual(c.marshal_value([1, 2, 3]), [1, 2, 3])

    def test_serialize_value(self):

        c = Collection(Integer())
        self.assertEqual(c.serialize_value([1, 2, 3]), [1, 2, 3])

    def test_validate_iterates_type(self):

        c = Collection(Integer())
        with self.assertRaises(ValidationError):
            c.validate([1, '2', 3])

    def test_collection_requires_list_type(self):

        c = Collection(Integer())
        with self.assertRaises(ValidationError):
            c.validate('foo')

    def test_collection_requires_valid_inner_type(self):

        with self.assertRaises(TypeError):
            Collection(object())


class NestedTypeTests(unittest.TestCase):

    def test_nested_requires_valid_mapping_type(self):

        with self.assertRaises(TypeError):
            nested = Nested(mapped=list())
            nested.mapping

    def test_nested_type_sets_role(self):

        role = Role('foo')
        mapping = Mapping()
        nested = Nested(mapped=mapping, role=role)
        self.assertEqual(nested.role, role)

    def test_nested_type_with_core_mapping_type(self):

        mapping = Mapping()
        nested = Nested(mapped=mapping)
        self.assertEqual(nested.mapping, mapping)

    def test_set_new_mapping_on_nested_type(self):

        mapping = Mapping()
        new_mapping = Mapping()

        nested = Nested(mapped=mapping)
        nested.mapping = new_mapping
        self.assertEqual(nested.mapping, new_mapping)

    def test_get_mapping_with_no_role(self):

        mapping = Mapping()
        nested = Nested(mapped=mapping)
        self.assertEqual(nested.get_mapping(), mapping)

    def test_get_mapping_with_role_set(self):

        name, email = TypeMapper('email', String()), TypeMapper('name', String())

        role = Role('foo', 'name')
        mapping = Mapping(name, email)
        nested = Nested(mapped=mapping, role=role)

        mapped = nested.get_mapping()
        self.assertNotEqual(mapped, mapping)

    def test_marshal_value(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name, email = TypeMapper('email', String()), TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)
        output = nested.marshal_value(Inner())
        exp = {
            'name': 'foo',
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_serialize_value(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name, email = TypeMapper('email', String()), TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)
        output = nested.serialize_value(Inner())
        exp = {
            'name': 'foo',
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_serialze_value_with_role(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name = TypeMapper('email', String())
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))
        output = nested.serialize_value(Inner())
        exp = {
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_marshal_value_with_role(self):

        class Inner(object):

            name = 'foo'
            email = 'bar@bar.com'

        name = TypeMapper('email', String())
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))
        output = nested.marshal_value(Inner())
        exp = {
            'email': 'bar@bar.com'
        }
        self.assertDictEqual(output, exp)

    def test_nested_validation_validates_mapped_fields_marshal(self):

        name = TypeMapper('email', String(), 'email_source')
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping)

        output = nested.validate({
            'name': 'foo',
            'email': 'foo@bar.com'
        })
        self.assertTrue(output)

        run = lambda: nested.validate({
            'name': 123,
            'email': 'foo@bar.com'
        })
        self.assertRaises(ValidationError, run)

    def test_nested_marshal_validation_with_role(self):
        """When a field is of an invlaid type, but is not included in the
        role passed to a nested type, the field should be ignored
        """

        name = TypeMapper('email', String(), 'email_source')
        email = TypeMapper('name', String())
        mapping = Mapping(name, email)

        nested = Nested(mapped=mapping, role=Role('email_only', 'email'))

        output = nested.validate({
            'name': 123,
            'email': 'foo@bar.com'
        })
        self.assertTrue(output)

    def test_import_by_string_relative(self):
        nested = Nested(mapped='ImportByStringMapping')

        self.assertEqual(nested.mapping, ImportByStringMapping)

    def test_import_by_string_absolute(self):
        nested = Nested(mapped='kim.tests.test_types.ImportByStringMapping')

        self.assertEqual(nested.mapping, ImportByStringMapping)


class DateTypeTests(unittest.TestCase):

    def test_validate_wrong_type(self):

        my_type = Date()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_for_marhsal_wrong_format(self):

        my_type = Date()
        with self.assertRaises(ValidationError):
            my_type.validate('2014-04-ASDFSD')

    def test_validate_valid(self):

        my_type = Date()
        self.assertTrue(my_type.validate('2014-04-07'))

    def test_serialize(self):
        value = date(2014, 4, 7)
        my_type = Date()
        result = my_type.serialize_value(value)

        self.assertEqual(result, '2014-04-07')

    def test_marshal(self):
        value = '2014-04-07'

        my_type = Date()
        result = my_type.marshal_value(value)

        self.assertEqual(result, date(2014, 4, 7))


class DateTimeTypeTests(unittest.TestCase):

    def test_validate_wrong_type(self):

        my_type = DateTime()
        with self.assertRaises(ValidationError):
            my_type.validate(0)

    def test_validate_for_marhsal_wrong_format(self):

        my_type = DateTime()
        with self.assertRaises(ValidationError):
            my_type.validate('2014-04-ASDFSD')

    def test_validate_valid(self):

        my_type = DateTime()
        self.assertTrue(my_type.validate('2014-04-07T05:06:05+00:00'))

    def test_validate_when_none(self):

        my_type = DateTime(required=False)
        self.assertTrue(my_type.validate(None))

    def test_serialize(self):
        value = datetime(2014, 4, 7, 5, 6, 5, tzinfo=Utc())
        my_type = DateTime()
        result = my_type.serialize_value(value)

        self.assertEqual(result, '2014-04-07T05:06:05+00:00')

    def test_marshal(self):
        value = '2014-04-07T05:06:05+00:00'

        my_type = DateTime()
        result = my_type.marshal_value(value)

        self.assertEqual(result, datetime(2014, 4, 7, 5, 6, 5, tzinfo=Utc()))


class RegexpTypeTests(unittest.TestCase):
    def test_validate_no_match(self):

        my_type = Regexp(pattern=re.compile('[0-9]+'))
        with self.assertRaises(ValidationError):
            my_type.validate('hello')

    def test_validate_valid(self):

        my_type = Regexp(pattern=re.compile('[0-9]+'))
        self.assertTrue(my_type.validate('1234'))

    def test_validate_when_none(self):

        my_type = Regexp(required=False)
        self.assertTrue(my_type.validate(None))


class EmailTypeTests(unittest.TestCase):
    def test_validate_no_match(self):

        my_type = Email()
        with self.assertRaises(ValidationError):
            my_type.validate('hello')

    def test_validate_valid(self):

        my_type = Email()
        self.assertTrue(my_type.validate('jack@gmail.com'))


class FloatTypeTests(unittest.TestCase):

    def test_validate_requires_valid_float_type(self):

        my_type = Float()
        with self.assertRaises(ValidationError):
            my_type.validate('')

    def test_validate_float_type(self):

        my_type = Float()
        self.assertTrue(my_type.validate(1.343))

    def test_serialize(self):
        my_type = Float()
        result = my_type.serialize_value(1.343)

        self.assertEqual(result, 1.343)

    def test_marshal(self):
        my_type = Float()
        result = my_type.marshal_value(1.343)

        self.assertEqual(result, 1.343)

    def test_validate_requires_valid_float_type_as_string(self):

        my_type = Float(as_string=True)
        with self.assertRaises(ValidationError):
            my_type.validate('abc')

    def test_validate_for_marhsal_float_type_as_string(self):

        my_type = Float(as_string=True)
        self.assertTrue(my_type.validate("1.343"))

    def test_validate_when_none(self):

        my_type = Float(required=False)
        self.assertTrue(my_type.validate(None))

    def test_serialize_as_string(self):
        my_type = Float(as_string=True)
        result = my_type.serialize_value(1.343)

        self.assertEqual(result, "1.343")

    def test_marshal_as_string(self):
        my_type = Float(as_string=True)
        result = my_type.marshal_value("1.343")

        self.assertEqual(result, 1.343)

class DecimalTypeTests(unittest.TestCase):

    def test_validate_requires_valid_decimal_type_as_string(self):

        my_type = Decimal()
        with self.assertRaises(ValidationError):
            my_type.validate('')

    def test_validate_requires_valid_decimal_type(self):

        my_type = Decimal()
        with self.assertRaises(ValidationError):
            my_type.validate(1)

    def test_validate_decimal_type(self):

        my_type = Decimal()
        self.assertTrue(my_type.validate("1.343"))

    def test_serialize(self):
        my_type = Decimal()
        result = my_type.serialize_value(decimal.Decimal("1.343"))

        self.assertEqual(result, "1.34300")

    def test_marshal(self):
        my_type = Decimal()
        result = my_type.marshal_value("1.343")

        self.assertEqual(result, decimal.Decimal("1.343"))

    def test_precision(self):
        my_type = Decimal(precision=2)
        result = my_type.serialize_value(decimal.Decimal("1.347"))

        self.assertEqual(result, "1.35")

    def test_validate_when_none(self):

        my_type = Decimal(required=False)
        self.assertTrue(my_type.validate(None))
