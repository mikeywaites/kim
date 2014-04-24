import unittest
import mock

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

    def test_type_mapper_default_overrides_type_default(self):

        mapped_type = TypeMapper('email', String(),
                                 default=123)

        self.assertEqual(mapped_type.default, 123)

    def test_validate(self):
        mockedtype = mock.MagicMock()
        mapped_type = TypeMapper('email', mockedtype,
                                 source='email_address')

        self.assertTrue(mapped_type.validate('foo'))
        self.assertTrue(mockedtype.validate.called)

