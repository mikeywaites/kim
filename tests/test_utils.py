#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim1.utils import is_valid_type, is_role
from kim1.types import BaseType
from kim1.roles import Role, BaseRole


class UtilTests(unittest.TestCase):

    def test_is_valid_type(self):

        class MyType(BaseType):
            pass

        class NotAType(object):
            pass

        self.assertTrue(is_valid_type(BaseType()))
        self.assertTrue(is_valid_type(MyType()))
        self.assertFalse(is_valid_type(NotAType()))

    def test_is_role_instance(self):

        class NotARole(object):
            pass

        class MyRole(BaseRole):
            pass

        self.assertTrue(is_role(MyRole()))
        self.assertTrue(is_role(BaseRole()))
        self.assertTrue(is_role(Role('public')))
        self.assertFalse(is_role(NotARole()))
