#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.validators import Validator, ValidationError
from kim.types import String, MappedType


class MyValidator(Validator):

    def validate(self, field_type, value):

        if not value == "foo":
            return False

        return True


class ValidatorTests(unittest.TestCase):

    def test_validator_must_implement_validate_method(self):

        class MyValidator(Validator):

            pass

        v = MyValidator()
        with self.assertRaises(NotImplementedError):
            v.run(MappedType('foo', String()), 'foo')
