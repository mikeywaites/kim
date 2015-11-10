# kim/pipelines/string.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import pipe
from .marshaling import MarshalPipeline
from .serialization import SerializePipeline

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
            wrapped_field.marshal(datum, _output, parent_session=session)
            result = _output[wrapped_field.opts.source]
            output.append(result)
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
        wrapped_field.serialize(datum, _output, parent_session=session)
        result = _output[wrapped_field.name]
        output.append(result)

    session.data = output
    return session.data


class CollectionMarshalPipeline(MarshalPipeline):

    output_pipes = [marshall_collection, ] + MarshalPipeline.output_pipes


class CollectionSerializePipeline(SerializePipeline):

    process_pipes = [serialize_collection, ] + SerializePipeline.process_pipes
