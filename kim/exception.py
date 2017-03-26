# kim/exception.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class KimException(Exception):
    """Base Exception for all Kim exception types."""

    def __init__(self, message, *args, **kwargs):

        self.message = message
        super(KimException, self).__init__(message, *args, **kwargs)


class MapperError(KimException):
    """MapperError is raised from a mapper that was unable to instantiate correctly."""
    pass


class MappingInvalid(KimException):

    def __init__(self, errors, *args, **kwargs):
        self.errors = errors
        super(MappingInvalid, self).__init__('Mapping invalid', *args, **kwargs)


class RoleError(KimException):
    pass


class FieldOptsError(KimException):
    pass


class FieldError(KimException):
    pass


class FieldInvalid(KimException):
    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop('field')
        super(FieldInvalid, self).__init__(*args, **kwargs)


class StopPipelineExecution(KimException):
    pass
