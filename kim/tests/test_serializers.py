#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.exceptions import RoleNotFound
from kim.serializers import Field, Serializer
from kim.types import String, Integer, TypeMapper
from kim.roles import whitelist


class SerializerTests(unittest.TestCase):
    def test_serializer(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        mapping = ASerializer().__mapping__

        self.assertEqual(len(mapping.fields), 2)

        first_field = mapping.fields[0]
        self.assertTrue(isinstance(first_field, TypeMapper))
        self.assertTrue(isinstance(first_field.base_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, TypeMapper))
        self.assertTrue(isinstance(second_field.base_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'c')

    def test_serializer_subclassing(self):
        class ABaseSerializer(Serializer):
            a = Field(String)
            b = Field(Integer, source='c')

        class ASubclassedSerializer(ABaseSerializer):
            d = Field(String)

        mapping = ASubclassedSerializer().__mapping__

        self.assertEqual(len(mapping.fields), 3)

        first_field = mapping.fields[0]
        self.assertTrue(isinstance(first_field, TypeMapper))
        self.assertTrue(isinstance(first_field.base_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, TypeMapper))
        self.assertTrue(isinstance(second_field.base_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'c')

        third_field = mapping.fields[2]
        self.assertTrue(isinstance(third_field, TypeMapper))
        self.assertTrue(isinstance(third_field.base_type, String))
        self.assertEqual(third_field.name, 'd')
        self.assertEqual(third_field.source, 'd')

    def test_serializer_subclassing_shadowing(self):
        class ABaseSerializer(Serializer):
            a = Field(String)
            b = Field(Integer, source='c')

        class ASubclassedSerializer(ABaseSerializer):
            b = Field(Integer, source='e')
            d = Field(String)

        mapping = ASubclassedSerializer().__mapping__

        self.assertEqual(len(mapping.fields), 3)

        first_field = mapping.fields[0]
        self.assertTrue(isinstance(first_field, TypeMapper))
        self.assertTrue(isinstance(first_field.base_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, TypeMapper))
        self.assertTrue(isinstance(second_field.base_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'e')

        third_field = mapping.fields[2]
        self.assertTrue(isinstance(third_field, TypeMapper))
        self.assertTrue(isinstance(third_field.base_type, String))
        self.assertEqual(third_field.name, 'd')
        self.assertEqual(third_field.source, 'd')

    def test_serialize(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        s = ASerializer({'a': 'hello', 'c': 123})

        result = s.serialize()
        self.assertEqual(result, {'a': 'hello', 'b': 123})

    def test_marshal(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        s = ASerializer(input={'a': 'hello', 'b': 123})

        result = s.marshal()
        self.assertEqual(result, {'a': 'hello', 'c': 123})

    def test_serializer_opts_with_role(self):

        public = whitelist('public', 'a')

        class MySerializer(Serializer):

            a = Field(String())
            b = Field(String())

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()
        exp = {
            'public': public
        }
        self.assertEqual(serializer.opts.roles, exp)

    def test__get_mapping_with_no_role_specified(self):

        name = Field(String())
        email = Field(String())

        class MySerializer(Serializer):

            a = name
            b = email

        serializer = MySerializer()

        mapped = serializer.get_mapping()
        field1, field2 = mapped.fields[0], mapped.fields[1]
        self.assertEqual(name.field_type, field1.base_type)
        self.assertEqual(email.field_type, field2.base_type)

    def test_get_mapping_with_role_name(self):

        public = whitelist('public', 'email')

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()

        mapped = serializer.get_mapping(role='public')
        self.assertEqual(len(mapped.fields), 1)
        self.assertEqual(mapped.fields[0].name, 'email')

    def test_get_mapping_with_invalid_role_name_raies_role_not_found(self):

        public = whitelist('public', 'email')

        name = Field(String())
        email = Field(String())

        class MySerializer(Serializer):

            a = name
            b = email

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()
        with self.assertRaises(RoleNotFound):
            serializer.get_mapping(role='not_a_role')

    def test_get_mapping_with_role_instance(self):

        public = whitelist('public', 'email')

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()
        name_role = whitelist('name_role', 'name')

        mapped = serializer.get_mapping(role=name_role)
        self.assertEqual(len(mapped.fields), 1)
        self.assertEqual(mapped.fields[0].name, 'name')
