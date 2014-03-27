#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.roles import Role, create_mapping_from_role, whitelist, blacklist
from kim.mapping import Mapping
from kim import types


class MyCustomMapping(Mapping):
    pass


class RoleTests(unittest.TestCase):

    def test_role_requires_name(self):

        with self.assertRaises(TypeError):
            Role()

    def test_role_name_correctly_set(self):

        role = Role('name', 'field_a')
        self.assertEqual(role.name, 'name')

    def test_field_names_correctly_set(self):

        role = Role('name', 'field_a', 'field_b')
        self.assertEqual(role.field_names, ('field_a', 'field_b'))

    def test_set_whitelist_option(self):

        role = Role('name', whitelist=False)
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

        mapping = MyCustomMapping('users', types.String('name'))
        role = Role('public', 'name')
        mapped = create_mapping_from_role(role, mapping)
        self.assertIsInstance(mapped, MyCustomMapping)

    def test_create_mapping_from_role(self):
        name = types.String('name')
        email = types.String('email')

        mapping = MyCustomMapping('users',
                                  name,
                                  email)
        role = Role('public', 'name')

        mapped = create_mapping_from_role(role, mapping)
        self.assertIn(name, mapped.fields)
        self.assertNotIn(email, mapped.fields)

    def test_whitelist_utility_function(self):

        role = whitelist('name', ['name'])
        self.assertEqual(role.name, 'name')
        self.assertEqual(role.field_names, ('name',))
        self.assertTrue(role.whitelist)

    def test_blacklist_utility_funcation(self):

        role = blacklist('name', ['name'])
        self.assertEqual(role.name, 'name')
        self.assertEqual(role.field_names, ('name',))
        self.assertFalse(role.whitelist)
