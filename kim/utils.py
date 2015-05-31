# kim/util.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


_creation_order = 1


def set_creation_order(instance):
    """Assign a '_creation_order' sequence to the given instance.
    This allows multiple instances to be sorted in order of creation
    (typically within a single thread; the counter is not particularly
    threadsafe).
    """
    global _creation_order
    instance._creation_order = _creation_order
    _creation_order += 1


def attr_or_key(obj, name):
    """attempt to use getattr to access an attribute of obj, if that fails
    assume obj support key based look ups like a dict.

    """

    try:
        return getattr(obj, name)
    except AttributeError:
        return obj.get(name)
