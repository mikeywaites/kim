# kim/util.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


_creation_order = 1

from collections import defaultdict


def set_creation_order(instance):
    """Assign a '_creation_order' sequence to the given instance.
    This allows multiple instances to be sorted in order of creation
    (typically within a single thread; the counter is not particularly
    threadsafe).
    """
    global _creation_order
    instance._creation_order = _creation_order
    _creation_order += 1


def _attr_or_key(obj, name):
    if isinstance(obj, dict):
        return obj.get(name)
    else:
        return getattr(obj, name, None)


def _set_attr_or_key(obj, name, value):
    if isinstance(obj, dict):
        obj[name] = value
    else:
        setattr(obj, name, value)


def attr_or_key(obj, name):
    """attempt to use getattr to access an attribute of obj, if that fails
    assume obj support key based look ups like a dict.

    Supports dot syntax to span nested objects/dicts eg 'foo.bar.baz'
    """
    components = name.split('.')
    for component in components:
        obj = _attr_or_key(obj, component)
    return obj


def set_attr_or_key(obj, name, value):
    """attempt to use getattr to access an attribute of obj, if that fails
    assume obj support key based look ups like a dict.

    Supports dot syntax to span nested objects/dicts eg 'foo.bar.baz'
    """
    components = name.split('.')
    for component in components[:-1]:
        obj = _attr_or_key(obj, component)
    _set_attr_or_key(obj, components[-1], value)


def recursive_defaultdict():
    """A simple recurrsive version of ``collections.defaultdict``

    """
    return defaultdict(recursive_defaultdict)
