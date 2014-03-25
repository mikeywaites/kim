#!/usr/bin/python
# -*- coding: utf-8 -*-


class KimGoneWrong(Exception):
    pass


class MappingError(KimGoneWrong):
    pass


class FieldError(KimGoneWrong):
    pass


class ValidatorTypeError(KimGoneWrong):
    pass


class ValidationError(KimGoneWrong):
    pass
