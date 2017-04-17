# kim/pipelines/nested.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.utils import attr_or_key

from .base import pipe
from .marshaling import MarshalPipeline
from .serialization import SerializePipeline


def _call_getter(session):
    if session.field.opts.getter:
        result = session.field.opts.getter(session)
        return result


@pipe()
def marshal_nested(session):
    """Marshal data using the nested mapper defined on this field.

    There are 6 possible scenarios, depending on the security setters and
    presence of a getter function

    * Getter function returns an object and no updates are allowed - Return the
      object immediately
    * Getter function returns an object and updates are allowed - Call the
      nested mapper with the object to update it
    * Object already exists, getter function returns None/does not exist and
      in place updates are allowed - Call the nested mapper with the existing
      object to update it
    * Getter function returns None/does not exist and creation of new objects
      is allowed - Call the nested mapper to create a new object
    * Getter function returns None/does not exist and creation of new objects
      is not allowed, nor are in place updates - Raise an exception.
    * Object already exists, getter function returns None/does not exist and
      partial updates are allowed - Call the nested mapper with the existing object
      to update it

    :param session: Kim pipeline session instance
    """

    resolved = _call_getter(session)

    partial = session.mapper_session.partial
    parent_mapper = session.mapper

    if session.parent and session.parent.nested_mapper:
        nested_mapper_class = session.parent.nested_mapper
    else:
        nested_mapper_class = session.field.get_mapper(as_class=True)

    if resolved is not None:
        if session.field.opts.allow_updates:
            nested_mapper = nested_mapper_class(
                data=session.data, obj=resolved, partial=partial,
                parent=parent_mapper)
            session.data = nested_mapper.marshal(role=session.field.opts.role)
        else:
            session.data = resolved
    else:
        existing_value = attr_or_key(session.output, session.field.name)
        if (session.field.opts.allow_updates_in_place or
                session.field.opts.allow_partial_updates) and \
                existing_value is not None:
            nested_mapper = nested_mapper_class(
                data=session.data, obj=existing_value, partial=partial,
                parent=parent_mapper)
            session.data = nested_mapper.marshal(role=session.field.opts.role)
        elif session.field.opts.allow_create:
            nested_mapper = nested_mapper_class(
                data=session.data, partial=partial, parent=parent_mapper)
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

    # Grab the Mapper defined for the nested field and call serialize()
    if session.parent and session.parent.nested_mapper:
        nested_mapper = session.parent.nested_mapper(obj=session.data)
    else:
        nested_mapper = session.field.get_mapper(obj=session.data)

    session.data = nested_mapper.serialize(role=session.field.opts.role)

    return session.data


class NestedMarshalPipeline(MarshalPipeline):
    """NestedMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.nested.marshal_nested`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    output_pipes = [marshal_nested, ] + MarshalPipeline.output_pipes


class NestedSerializePipeline(SerializePipeline):
    """NestedSerializePipeline

    .. seealso::
        :func:`kim.pipelines.nested.serialize_nested`
        :class:`kim.pipelines.serialization.SerializePipeline`
    """

    process_pipes = [serialize_nested, ] + SerializePipeline.process_pipes
