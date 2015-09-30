import unittest
from datetime import date, datetime

from iso8601.iso8601 import Utc

from kim1.serializers import Serializer, Field
from kim1.types import (String, Collection, Nested, Integer, Email, Date,
    DateTime)
from kim1.exceptions import ConfigurationError


class ErrorHandlingAcceptanceTests(unittest.TestCase):
    def test_field_wrapper_not_used_instance(self):
        def make_serializer():
            class TestSerializer(Serializer):
                status = Integer()

        self.assertRaises(ConfigurationError, make_serializer)

    def test_field_wrapper_not_used_class(self):
        def make_serializer():
            class TestSerializer(Serializer):
                status = Integer

        self.assertRaises(ConfigurationError, make_serializer)