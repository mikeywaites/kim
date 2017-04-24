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


def _attr_or_key(obj, name, _isinstance=isinstance, _dict=dict, getter=getattr):
    """Attempt to return the attr stored against the specified name from a dict or
    from an attribute on an object.

    :param obj: The obj to request the attribute from
    :param name: The name of the attribute or key on the obj
    :param _isinstance: isinstance built-in
    :param _dict: isinstance built-in
    :param _getattr: getattr built-in

    Note
    ~~~~~

    Just a brief word on the odd re-assignment of built in functions to kwargs.
    Given the huge number of times this function is called in the benchmarking suite,
    Python having to call the builtins from the global scope is actually fairly slow.

    By assigning them to kwargs they will be compiled in the module's scope and will
    be found using the LOAD_FAST lookup.  You can read more about this technique here
    http://jamesls.com/micro-optimizations-in-python-code-speeding-up-lookups.html

    This technique yielded between 3-5% performance increase so we felt it was worth the
    trade of with it being pretty weird.

    .. version-added: 1.1.0
    """
    if _isinstance(obj, _dict):
        return obj.get(name)
    else:
        return getter(obj, name, None)


def _set_attr_or_key(obj, name, value, _isinstance=isinstance, _dict=dict, setter=setattr):
    """Attempt to set the attr stored against the specified name on a dict or
    on an attribute on an object.

    :param obj: The obj to request the attribute from
    :param name: The name of the attribute or key on the obj
    :param value: The name value being set
    :param _isinstance: isinstance built-in
    :param _dict: isinstance built-in
    :param setter: setattr built-in

    Note
    ~~~~~

    Just a brief word on the odd re-assignment of built in functions to kwargs.
    Given the huge number of times this function is called in the benchmarking suite,
    Python having to call the builtins from the global scope is actually fairly slow.

    By assigning them to kwargs they will be compiled in the module's scope and will
    be found using the LOAD_FAST lookup.  You can read more about this technique here
    http://jamesls.com/micro-optimizations-in-python-code-speeding-up-lookups.html

    This technique yielded between 3-5% performance increase so we felt it was worth the
    trade of with it being pretty weird.

    .. version-added: 1.1.0
    """
    if _isinstance(obj, _dict):
        obj[name] = value
    else:
        setter(obj, name, value)


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


def attr_or_key_update(obj, value):
    """If obj is a dict, add keys from value to it with update(),
    otherwise use setattr to set every attribute from value on obj
    """
    if obj is not None and value is not None:
        if isinstance(obj, dict):
            obj.update(value)
        else:
            for k, v in value.items():
                setattr(obj, k, v)


def recursive_defaultdict():
    """A simple recurrsive version of ``collections.defaultdict``

    """
    return defaultdict(recursive_defaultdict)
