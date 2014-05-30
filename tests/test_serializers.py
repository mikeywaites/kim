#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import mock

from kim.exceptions import RoleNotFound, ValidationError, MappingErrors
from kim.serializers import Field, Serializer
from kim.types import String, Integer, Nested
from kim.fields import Field
from kim.roles import whitelist


class SerializerTests(unittest.TestCase):

    def test_serializer(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        mapping = ASerializer().__mapping__

        self.assertEqual(len(mapping.fields), 2)

        first_field = mapping.fields[0]
        self.assertTrue(isinstance(first_field, Field))
        self.assertTrue(isinstance(first_field.field_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, Field))
        self.assertTrue(isinstance(second_field.field_type, Integer))
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
        self.assertTrue(isinstance(first_field, Field))
        self.assertTrue(isinstance(first_field.field_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, Field))
        self.assertTrue(isinstance(second_field.field_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'c')

        third_field = mapping.fields[2]
        self.assertTrue(isinstance(third_field, Field))
        self.assertTrue(isinstance(third_field.field_type, String))
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
        self.assertTrue(isinstance(first_field, Field))
        self.assertTrue(isinstance(first_field.field_type, String))
        self.assertEqual(first_field.name, 'a')
        self.assertEqual(first_field.source, 'a')

        second_field = mapping.fields[1]
        self.assertTrue(isinstance(second_field, Field))
        self.assertTrue(isinstance(second_field.field_type, Integer))
        self.assertEqual(second_field.name, 'b')
        self.assertEqual(second_field.source, 'e')

        third_field = mapping.fields[2]
        self.assertTrue(isinstance(third_field, Field))
        self.assertTrue(isinstance(third_field.field_type, String))
        self.assertEqual(third_field.name, 'd')
        self.assertEqual(third_field.source, 'd')

    def test_serialize(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        s = ASerializer()

        result = s.serialize({'a': 'hello', 'c': 123})
        self.assertEqual(result, {'a': 'hello', 'b': 123})

    def test_marshal(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        s = ASerializer()

        result = s.marshal({'a': 'hello', 'b': 123})
        self.assertEqual(result, {'a': 'hello', 'c': 123})

    def test_serialize_to_json(self):
        class ASerializer(Serializer):
            a = Field(String())
            b = Field(Integer, source='c')

        s = ASerializer()

        result = s.json({'a': 'hello', 'c': 123})
        self.assertEqual(result, '{"a": "hello", "b": 123}')

    def test_serializer_opts_with_role(self):

        public = whitelist('a')

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

    def test_get_mapping_with_no_role_specified(self):

        name = Field(String())
        email = Field(String())

        class MySerializer(Serializer):

            a = name
            b = email

        serializer = MySerializer()

        mapped = serializer.get_mapping()
        field1, field2 = mapped.fields[0], mapped.fields[1]
        self.assertEqual(name.field_type, field1.field_type)
        self.assertEqual(email.field_type, field2.field_type)

    def test_get_mapping_with_role_name(self):

        public = whitelist('email')

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

        public = whitelist('email')

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

        public = whitelist('email')

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()
        name_role = whitelist('name')

        mapped = serializer.get_mapping(role=name_role)
        self.assertEqual(len(mapped.fields), 1)
        self.assertEqual(mapped.fields[0].name, 'name')

    def test_get_mapping_with_role_duplicate_name(self):

        public = whitelist('email2')

        class MySerializer(Serializer):

            email1 = Field(String(), name='email')
            email2 = Field(String(), name='email')

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()

        mapped = serializer.get_mapping(role='public')
        self.assertEqual(len(mapped.fields), 1)
        self.assertEqual(mapped.fields[0].name, 'email')
        self.assertEqual(mapped.fields[0].field_id, 'email2')

    def test_serialize_with_role(self):

        public = whitelist('email')

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()

        result = serializer.serialize({'email': 'foo', 'name': 'bar'},
                                      role='public')

        self.assertDictEqual(result, {'email': 'foo'})

    def test_marshal_with_role(self):

        public = whitelist('email')

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            class Meta:

                roles = {'public': public}

        serializer = MySerializer()

        result = serializer.marshal({'email': 'foo', 'name': 'bar'},
                                    role='public')
        self.assertDictEqual(result, {'email': 'foo'})

    def test_validate_method_called(self):
        mocked = mock.MagicMock()

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            validate_name = mocked

        serializer = MySerializer()

        serializer.marshal({'email': 'foo', 'name': 'bar'})

        mocked.assert_called_with(serializer, 'bar')

    def test_validate_method_failure(self):
        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            def validate_name(self, source_value):
                raise ValidationError()

        serializer = MySerializer()

        with self.assertRaises(MappingErrors):
            serializer.marshal({'email': 'foo', 'name': 'bar'})

    def test_fields_api(self):
        name_type = String()
        email_type = String()

        class MySerializer(Serializer):

            name = Field(name_type)
            email = Field(email_type)

        fields = MySerializer().fields

        self.assertEqual(fields['name'].field_type, name_type)
        self.assertEqual(fields['email'].field_type, email_type)

    def test_top_level_validate_method_called(self):
        mocked = mock.MagicMock()

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            validate = mocked

        serializer = MySerializer()

        serializer.marshal({'email': 'foo', 'name': 'bar'})

        mocked.assert_called_with({'email': 'foo', 'name': 'bar'})

    def test_top_level_validate_method_failure(self):
        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())

            def validate(self, data):
                raise MappingErrors({'email': ['bla']})

        serializer = MySerializer()

        with self.assertRaises(MappingErrors):
            serializer.marshal({'email': 'foo', 'name': 'bar'})

    def test_field_default_used(self):
        mocked = mock.MagicMock()

        class MySerializer(Serializer):

            name = Field(String(), required=False, default='this is a default')
            email = Field(String())

            validate = mocked

        serializer = MySerializer()

        serializer.marshal({'email': 'foo'})

        mocked.assert_called_with({'email': 'foo', 'name': 'this is a default'})

    def test_field_default_ignored(self):
        mocked = mock.MagicMock()

        class MySerializer(Serializer):

            name = Field(String(), default='this is a default')
            email = Field(String())

            validate = mocked

        serializer = MySerializer()

        serializer.marshal({'email': 'foo', 'name': 'default unused'})

        mocked.assert_called_with({'email': 'foo', 'name': 'default unused'})

    def test_nested_read_only_field_ignored_on_marshal(self):

        class CompanySerialzer(Serializer):
            name = Field(String())

        class MySerializer(Serializer):

            name = Field(String())
            email = Field(String())
            supplier = Field(Nested(CompanySerialzer),
                             required=False,
                             read_only=True)

        serializer = MySerializer()
        res = serializer.marshal({'email': 'foo', 'name': 'bar', 'supplier': 1})
        self.assertEqual(res, {'email': 'foo', 'name': 'bar'})
