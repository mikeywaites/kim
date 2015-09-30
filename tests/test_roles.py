#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim1.roles import Role, create_mapping_from_role, whitelist, blacklist
from kim1.mapping import Mapping
from kim1 import types
from kim1.fields import Field


class MyCustomMapping(Mapping):
    pass


class CustomRole(Role):
    pass


class RoleTests(unittest.TestCase):

    def test_field_names_correctly_set(self):

        role = Role('field_a', 'field_b')
        self.assertEqual(role.field_names, ('field_a', 'field_b'))

    def test_set_whitelist_option(self):

        role = Role(whitelist=False)
        self.assertFalse(role.whitelist)

    def test_membership_for_whitelist_role(self):

        role = Role('users', 'email', whitelist=True)
        self.assertTrue(role.membership('email'))
        self.assertFalse(role.membership('name'))

    def test_membership_for_blacklist_role(self):

        role = Role('users', 'email', whitelist=False)
        self.assertFalse(role.membership('email'))
        self.assertTrue(role.membership('name'))

    def test_create_role_mapping_uses_mapping_type(self):

        mapping = MyCustomMapping('users', Field('name', types.String()))
        role = Role('name')
        mapped = create_mapping_from_role(role, mapping)
        self.assertIsInstance(mapped, MyCustomMapping)

    def test_create_mapping_from_role(self):
        name = Field('name', types.String())
        email = Field('email', types.String())

        mapping = MyCustomMapping('users',
                                  name,
                                  email)
        role = Role('name')

        mapped = create_mapping_from_role(role, mapping)
        self.assertIn(name, mapped.fields)
        self.assertNotIn(email, mapped.fields)

    def test_create_mapping_from_role_duplicate_field_ids(self):
        email1 = Field('email', types.String(), field_id='email1')
        email2 = Field('email', types.String(), field_id='email2')

        mapping = MyCustomMapping('users',
                                  email1,
                                  email2)
        role = Role('email2')

        mapped = create_mapping_from_role(role, mapping)
        self.assertIn(email2, mapped.fields)
        self.assertNotIn(email1, mapped.fields)

    def test_whitelist_utility_function(self):

        role = whitelist('name')
        self.assertEqual(role.field_names, ('name',))
        self.assertTrue(role.whitelist)

    def test_blacklist_utility_funcation(self):

        role = blacklist('name')
        self.assertEqual(role.field_names, ('name',))
        self.assertFalse(role.whitelist)

    def test_create_role_with_custom_base(self):

        role = whitelist('bar', role_base=CustomRole)
        self.assertIsInstance(role, CustomRole)
