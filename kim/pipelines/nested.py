# kim/pipelines/nested.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (pipe, Input, Output,
                   marshal_input_pipe, marshal_output_pipe,
                   serialize_input_pipe, serialize_output_pipe)
from kim.utils import attr_or_key


def _call_getter(session):
    if session.field.opts.getter:
        result = session.field.opts.getter(session.field, session.data)
        return result


@pipe()
def marshal_nested(session):
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
       is not allowed, nor are in place updates. Raise an exception.

    :param session: Kim pipeline session instance

    """

    resolved = _call_getter(session)

    if resolved is not None:
        if session.field.opts.allow_updates:
            nested_mapper = session.field.get_mapper(
                data=session.data, obj=resolved)
            session.data = nested_mapper.marshal(role=session.field.opts.role)
        else:
            session.data = resolved
    else:
        if session.field.opts.allow_updates_in_place:
            existing_value = attr_or_key(session.output, session.field.name)
            # If no existing value is found in the output, this is probably
            # a nested collection with more objects in the json input
            # than already exist
            if not existing_value:
                raise session.field.invalid('invalid_collection_length')
            nested_mapper = session.field.get_mapper(
                data=session.data, obj=existing_value)
            session.data = nested_mapper.marshal(role=session.field.opts.role)
        elif session.field.opts.allow_create:
            nested_mapper = session.field.get_mapper(data=session.data)
            session.data = nested_mapper.marshal(role=session.field.opts.role)
        else:
            raise session.field.invalid(error_type='not_found')

    return session.data


@pipe(run_if_none=True)
def serialize_nested(session):
    """Serialize data using the nested mapper defined on this field.

    :param session: Kim pipeline session instance

    """

    if session.data is None:
        session.data = session.field.opts.null_default
        return session.data

    nested_mapper = session.field.get_mapper(obj=session.data)
    session.data = nested_mapper.serialize(role=session.field.opts.role)

    return session.data


class NestedInput(Input):

    input_pipes = marshal_input_pipe
    output_pipes = [marshal_nested] + marshal_output_pipe


class NestedOutput(Output):

    input_pipes = serialize_input_pipe
    process_pipes = [
        serialize_nested
    ]
    output_pipes = serialize_output_pipe
