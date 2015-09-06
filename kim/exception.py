# kim/exception.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class KimException(Exception):

    def __init__(self, message, *args, **kwargs):

        self.message = message
        super(KimException, self).__init__(message, *args, **kwargs)


class MapperError(KimException):
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
    pass


class StopPipelineExecution(KimException):
    pass
