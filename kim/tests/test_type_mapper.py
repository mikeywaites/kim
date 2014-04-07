import unittest

from kim.types import String
from kim.exceptions import ValidationError
from kim.type_mapper import TypeMapper


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

    def test_marshal_value(self):

        mapped_type = TypeMapper('email', String(), source='email_address')
        self.assertEqual(mapped_type.marshal_value('foo'), 'foo')

    def test_serialize_value(self):

        mapped_type = TypeMapper('email', String(), source='email_address')
        self.assertEqual(mapped_type.serialize_value('foo'), 'foo')

    def test_validate_raises_error_when_required_and_value_null(self):

        mapped_type = TypeMapper('email', String(),
                                 source='email_address',
                                 required=True)
        with self.assertRaises(ValidationError):
            mapped_type.validate('')

    def test_validate_not_allow_none(self):
        mapped_type = TypeMapper('email', String(),
                                 source='email_address',
                                 allow_none=False,
                                 required=False)

        with self.assertRaises(ValidationError):
            mapped_type.validate(None)

    def test_validate_allow_none(self):

        mapped_type = TypeMapper('email', String(),
                                 source='email_address',
                                 required=False,
                                 allow_none=True)

        self.assertTrue(mapped_type.validate(None))

    def test_validate_mapped_type(self):
        mapped_type = TypeMapper('email', String(),
                                 source='email_address',
                                 required=True,
                                 allow_none=False)

        self.assertTrue(mapped_type.validate('foo'))

    def test_type_mapper_default_overrides_type_default(self):

        mapped_type = TypeMapper('email', String(),
                                 default=123)

        self.assertEqual(mapped_type.default, 123)

    def test_set_allow_none(self):
        mapped_type = TypeMapper('email', String(),
                                 allow_none=False)

        self.assertEqual(mapped_type.allow_none, False)
