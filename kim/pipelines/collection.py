# kim/pipelines/string.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.exception import FieldInvalid
from kim.utils import attr_or_key

from .base import pipe
from .marshaling import MarshalPipeline
from .serialization import SerializePipeline


@pipe(run_if_none=True)
def marshall_collection(session):
    """iterate over each item in ``data`` and marshal the item through the
    wrapped field defined for this collection

    :param session: Kim pipeline session instance

    TODO(mike) this should be called marshal_collection
    """
    wrapped_field = session.field.opts.field
    existing_value = attr_or_key(session.output, session.field.opts.source)

    output = []

    if session.data is not None:
        if not hasattr(session.data, '__iter__'):
            raise session.field.invalid('type_error')

        for i, datum in enumerate(session.data):
            _output = {}
            # If the object already exists, try to match up the existing elements
            # with those in the input json
            if existing_value is not None:
                try:
                    _output[wrapped_field.opts.source] = existing_value[i]
                except IndexError:
                    pass

            mapper_session = session.mapper.get_mapper_session(datum, _output)
            wrapped_field.marshal(mapper_session, parent_session=session)

            result = _output[wrapped_field.opts.source]
            output.append(result)

    session.data = output
    return session.data


@pipe()
def serialize_collection(session):
    """iterate over each item in ``data`` and serialize the item through the
    wrapped field defined for this collection

    :param session: Kim pipeline session instance

    """
    wrapped_field = session.field.opts.field
    field_name = wrapped_field.name
    output = []

    mapper_session = session.mapper.get_mapper_session(None, {})

    # If the wrapped field uses a mapper, fetch it once to avoid looking up the mapper
    # from the registry for each item in the collection.
    session.nested_mapper = getattr(
        wrapped_field,
        'get_mapper',
        lambda **kwargs: None)(as_class=True)

    for datum in session.data:
        mapper_session.data = datum
        mapper_session.output = {}
        wrapped_field.serialize(mapper_session, parent_session=session)
        output.append(mapper_session.output[field_name])

    session.data = output
    return session.data


@pipe()
def check_duplicates(session):
    """iterate over collection and check for duplicates if th unique_on FieldOpt has been
    set of this Collection field

    TODO(mike) This should only run if the wrapped field is a nested collection

    """
    data = session.data
    key = session.field.opts.unique_on
    if key:
        keys = [attr_or_key(a, key) for a in data]
        if len(keys) != len(set(keys)):
            raise session.field.invalid(error_type='duplicates')
    return data


class CollectionMarshalPipeline(MarshalPipeline):
    """CollectionMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.collection.check_duplicates`
        :func:`kim.pipelines.collection.marshal_collection`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    input_pipes = MarshalPipeline.input_pipes + [check_duplicates, marshall_collection]


class CollectionSerializePipeline(SerializePipeline):
    """CollectionSerializePipeline

    .. seealso::
        :func:`kim.pipelines.collection.serialize_collection`
        :class:`kim.pipelines.serialization.SerializePipeline`
    """

    process_pipes = [serialize_collection, ] + SerializePipeline.process_pipes
