# kim/pipelines/nested.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (Input, Output, marshal_input_pipe, marshal_output_pipe,
                   serialize_input_pipe, serialize_output_pipe)
from kim.utils import attr_or_key


def _call_getter(field, data):
    if field.opts.getter:
        result = field.opts.getter(field, data)
        return result


def marshal_nested(field, data, output):
    """Marshal data using the nested mapper defined on this field.
    """
    # 1. User has passed an id and no updates are allowed.
    #    Resolve the id to an object and return immediately
    # 2. User has passed an id and updates are allowed.
    #    Resolve the id to an object and call recursively to update it
    # 3. Object already exists, user has not passed an id and in place
    #    updates are allowed. Call recursively to update existing object.
    # 4. User has not passed an id and creation of new objects is allowed
    #    Call recursively to create a new object
    # 5. User has not passed an id and creation of new objects is not
    #    allowed, nor are in place updates. Raise an exception.

    resolved = _call_getter(field, data)

    if resolved is not None:
        if field.opts.allow_updates:
            nested_mapper = field.get_mapper(data=data, obj=resolved)
            return nested_mapper.marshal(role=field.opts.role)
        else:
            return resolved
    else:
        if field.opts.allow_updates_in_place:
            existing_value = attr_or_key(output, field.name)
            nested_mapper = field.get_mapper(data=data, obj=existing_value)
            return nested_mapper.marshal(role=field.opts.role)
        elif field.opts.allow_create:
            nested_mapper = field.get_mapper(data=data)
            return nested_mapper.marshal(role=field.opts.role)
        else:
            raise field.invalid('%s not found' % field.name)


def serialize_nested(field, data):
    """Serialize data using the nested mapper defined on this field.
    """

    nested_mapper = field.get_mapper(obj=data)
    return nested_mapper.serialize(role=field.opts.role)


class NestedInput(Input):

    input_pipes = marshal_input_pipe
    output_pipes = [marshal_nested] + marshal_output_pipe


class NestedOutput(Output):

    input_pipes = serialize_input_pipe
    process_pipes = [
        serialize_nested
    ]
    output_pipes = serialize_output_pipe
