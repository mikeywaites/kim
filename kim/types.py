#!/usr/bin/python
# -*- coding: utf-8 -*-


class TypeABC(object):

    def __init__(self, name, source):
        self.name = name
        self.source = source


class String(TypeABC):
    pass


class Integer(TypeABC):
    pass
