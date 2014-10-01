#!/usr/bin/python
# -*- coding: utf-8 -*-

from .roles import BaseRole

from collections import defaultdict


def is_valid_type(type_):
    """Validate that `type_` is an instance or subclass of
    :class:`kim.types.BaseType`.

    :param type_: an instance or subclass of :class:`kim.types.BaseType`

    :rtype: boolean
    :returns: True or False
    """
    from kim.types import BaseType

    return isinstance(type_, BaseType)


def is_role(role):
    """evaluate `role` and check wether its a valid role instance or
    valid role subclass.

    :rtype: boolean
    :returns: True or False
    """

    return isinstance(role, BaseRole)


def is_valid_field(field):
    from .fields import Field

    return isinstance(field, Field)


def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)