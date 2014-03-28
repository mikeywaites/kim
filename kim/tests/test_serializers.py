#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.serializers import Field, Serializer
from kim.types import String, Integer, MappedType


class SerializerTests(unittest.TestCase):
    def test_serializer(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        mapping = ASerializer().__mapping__

        self.assertEqual(len(mapping.fields), 2)

        first_field = mapping.fields[0]
        self.assertTrue(isinstance(first_field, MappedType))
        self.assertTrue(isinstance(first_field.base_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, MappedType))
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
        self.assertTrue(isinstance(first_field, MappedType))
        self.assertTrue(isinstance(first_field.base_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, MappedType))
        self.assertTrue(isinstance(second_field.base_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'c')

        third_field = mapping.fields[2]
        self.assertTrue(isinstance(third_field, MappedType))
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
        self.assertTrue(isinstance(first_field, MappedType))
        self.assertTrue(isinstance(first_field.base_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, MappedType))
        self.assertTrue(isinstance(second_field.base_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'e')

        third_field = mapping.fields[2]
        self.assertTrue(isinstance(third_field, MappedType))
        self.assertTrue(isinstance(third_field.base_type, String))
        self.assertEqual(third_field.name, 'd')
        self.assertEqual(third_field.source, 'd')
