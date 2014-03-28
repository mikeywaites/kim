#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.validators import Validator, validator
from kim.types import String


class MyValidator(Validator):

    def validate(self, field_type, value):

        if not value == "foo":
            return False

        return True


class ValidatorTests(unittest.TestCase):

    def test_validator_decorator(self):

        @validator()
        def my_validator(field_type, value):

            if not value == "bar":
                return False

            return True

        v = my_validator()
        import ipdb; ipdb.set_trace()
        v.run(String('foo'), 'baz')
