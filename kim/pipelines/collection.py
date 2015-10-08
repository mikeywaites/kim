# kim/pipelines/string.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (pipe, Input, Output, marshal_input_pipe, marshal_output_pipe,
                   serialize_input_pipe, serialize_output_pipe)
from kim.utils import attr_or_key


@pipe()
def marshall_collection(session):
    """iterate over each item in ``data`` and marshal the item through the
    wrapped field defined for this collection

    :param session: Kim pipeline session instance

    """
    wrapped_field = session.field.opts.field
    existing_value = attr_or_key(session.output, session.field.opts.source)

    output = []

    try:
        for i, datum in enumerate(session.data):
            _output = {}
            # If the object already exists, try to match up the existing elements
            # with those in the input json
            if existing_value is not None:
                try:
                    _output[wrapped_field.opts.source] = existing_value[i]
                except IndexError:
                    pass
            wrapped_field.marshal(datum, _output)
            output.append(_output[wrapped_field.opts.source])
    except TypeError:
        raise session.field.invalid('type_error')

    session.data = output
    return session.data


@pipe()
def serialize_collection(session):
    """iterate over each item in ``data`` and serialize the item through the
    wrapped field defined for this collection

    :param session: Kim pipeline session instance

    """
    wrapped_field = session.field.opts.field
    output = []

    for datum in session.data:
        _output = {}
        wrapped_field.serialize(datum, _output)
        result = _output[wrapped_field.name]
        output.append(result)

    session.data = output
    return session.data


class CollectionInput(Input):

    input_pipes = marshal_input_pipe
    output_pipes = [marshall_collection] + marshal_output_pipe


class CollectionOutput(Output):

    input_pipes = serialize_input_pipe
    process_pipes = [
        serialize_collection,
    ]
    output_pipes = serialize_output_pipe
