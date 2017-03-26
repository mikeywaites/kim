# kim/pipelines/datetime.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import iso8601

from .base import pipe, is_valid_choice
from .marshaling import MarshalPipeline
from .serialization import SerializePipeline


@pipe()
def is_valid_datetime(session):
    """Pipe used to determine if a value can be coerced to a datetime

    :param session: Kim pipeline session instance

    """

    if session.data is not None:
        try:
            session.data = iso8601.parse_date(session.data)
        except iso8601.ParseError:
            raise session.field.invalid(error_type='type_error')
    return session.data


@pipe()
def format_datetime(session):
    """convert datetime object to isoformat() datetime str
    """
    if session.data is not None:
        session.data = session.data.isoformat()
    return session.data


class DateTimeMarshalPipeline(MarshalPipeline):
    """DateTimeMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.datetime.is_valid_datetime`
        :func:`kim.pipelines.base.is_valid_choice`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    validation_pipes = \
        [is_valid_datetime, is_valid_choice] + MarshalPipeline.validation_pipes


class DateTimeSerializePipeline(SerializePipeline):
    """DateTimeSerializePipeline

    .. seealso::
        :func:`kim.pipelines.datetime.format_datetime`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """
    process_pipes = [format_datetime, ] + SerializePipeline.process_pipes


@pipe()
def cast_to_date(session):
    """cast session.data datetime object to a date() instance
    """
    if session.data is not None:
        session.data = session.data.date()
    return session.data


class DateMarshalPipeline(DateTimeMarshalPipeline):
    """DateMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.datetime.cast_to_date`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    process_pipes = [cast_to_date, ] + MarshalPipeline.process_pipes


class DateSerializePipeline(DateTimeSerializePipeline):
    """DateSerializePipeline

    .. seealso::
        :func:`kim.pipelines.serialization.SerializePipeline`
    """
    pass
