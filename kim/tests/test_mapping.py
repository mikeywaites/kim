#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from kim.mapping import Mapping


class FieldInterface(object):
    #TODO replace this with a proper field class

    pass


class MappingTest(unittest.TestCase):

    def test_add_initial_mapping(self):

        field_a = FieldInterface()

        initial = {'field_a': field_a}
        mapping = Mapping(**initial)

        exp = Mapping.collection()
        exp['field_a'] = field_a
        self.assertDictEqual(exp, mapping.mapped())

    def test_mapping_with_no_initial_mapping(self):

        mapping = Mapping()
        self.assertDictEqual(Mapping.collection(), mapping.mapped())

    def test_add_property_to_mapping(self):

        field_a = FieldInterface()
        mapping = Mapping()
        mapping.add('field_a', field_a)

        exp = Mapping.collection()
        exp['field_a'] = field_a

        self.assertDictEqual(exp, mapping.mapped())

    def test_add_property_overwrites_initial_property(self):
        field_a = FieldInterface()
        field_b = FieldInterface()

        initial = {'field_a': field_a}
        mapping = Mapping(**initial)
        mapping.add('field_a', field_b)

        exp = Mapping.collection()
        exp['field_a'] = field_b
        self.assertDictEqual(exp, mapping.mapped())
