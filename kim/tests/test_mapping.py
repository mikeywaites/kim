#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import pytest

from kim.mapping import Mapping


class FieldInterface(object):
    #TODO replace this with a proper field class

    pass


class MappingTest(unittest.TestCase):

    def test_add_initial_mapping(self):

        self.maxDiff = None
        field_a = FieldInterface()
        field_b = FieldInterface()

        initial = {'field_a': field_a}
        mapping = Mapping(**initial)

        exp = Mapping.collection()
        exp['field_a'] = field_a
        self.assertDictEqual(exp, mapping.mapped())
