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

    There are 5 possible scenarios, depending on the security setters and
    presence of a getter function:
    1. Getter function returns an object and no updates are allowed.
       Return the object immediately
    2. Getter function returns an object and updates are allowed.
       Call the nested mapper with the object to update it
    3. Object already exists, getter function returns None/does not exist and
       in place updates are allowed.
       Call the nested mapper with the existing object to update it
    4. Getter function returns None/does not exist and creation of new objects
       is allowed
       Call the nested mapper to create a new object
    5. Getter function returns None/does not exist and creation of new objects
       is not allowed, nor are in place updates. Raise an exception."""

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
            # If no existing value is found in the output, this is probably
            # a nested collection with more objects in the json input
            # than already exist
            if not existing_value:
                raise field.invalid('invalid_collection_length')
            nested_mapper = field.get_mapper(data=data, obj=existing_value)
            return nested_mapper.marshal(role=field.opts.role)
        elif field.opts.allow_create:
            nested_mapper = field.get_mapper(data=data)
            return nested_mapper.marshal(role=field.opts.role)
        else:
            raise field.invalid(error_type='not_found')


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
