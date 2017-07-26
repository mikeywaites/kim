# kim/pipelines/numeric.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from decimal import Decimal, InvalidOperation

from .base import pipe, is_valid_choice
from .marshaling import MarshalPipeline
from .serialization import SerializePipeline


@pipe()
def is_valid_integer(session):
    """Pipe used to determine if a value can be coerced to an int

    :param session: Kim pipeline session instance

    """

    try:
        session.data = int(session.data)
    except TypeError:
        raise session.field.invalid(error_type='type_error')
    except ValueError:
        raise session.field.invalid(error_type='type_error')
    return session.data


@pipe()
def bounds_check(session):
    """Pipe used to determine if a value is within the min and max bounds on
    the field

    :param session: Kim pipeline session instance

    """

    max_ = session.field.opts.max
    min_ = session.field.opts.min

    if max_ is not None and session.data > max_:
        raise session.field.invalid(error_type='out_of_bounds')
    if min_ is not None and session.data < min_:
        raise session.field.invalid(error_type='out_of_bounds')

    return session.data


class IntegerMarshalPipeline(MarshalPipeline):
    """IntegerMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.numeric.is_valid_integer`
        :func:`kim.pipelines.base.is_valid_choice`
        :func:`kim.pipelines.numeric.bounds_check`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    validation_pipes = \
        [is_valid_integer, is_valid_choice, bounds_check] + MarshalPipeline.validation_pipes


class IntegerSerializePipeline(SerializePipeline):
    """IntegerSerializePipeline

    .. seealso::
        :class:`kim.pipelines.serialization.SerializePipeline`
    """
    pass


@pipe()
def is_valid_decimal(session):
    """Pipe used to determine if a value can be coerced to a Decimal

    :param session: Kim pipeline session instance

    """
    try:
        return Decimal(session.data)
    except InvalidOperation:
        raise session.field.invalid(error_type='type_error')


@pipe()
def coerce_to_decimal(session):
    """Coerce str representation of a decimal into a valid Decimal object.
    """
    decimals = session.field.opts.precision
    precision = Decimal('0.' + '0' * (decimals - 1) + '1')
    session.data = Decimal(session.data).quantize(precision)
    return session.data


class DecimalMarshalPipeline(MarshalPipeline):
    """DecimalMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.numeric.is_valid_decimal`
        :func:`kim.pipelines.numeric.coerce_to_decimal`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    validation_pipes = [is_valid_decimal, bounds_check] + MarshalPipeline.validation_pipes
    process_pipes = [coerce_to_decimal] + MarshalPipeline.process_pipes


# TODO(mike) This should probably move to base
@pipe()
def to_string(session):
    """coerce decimal value into str so it's valid for json
    """
    if session.data is not None:
        session.data = str(session.data)
        return session.data


class DecimalSerializePipeline(SerializePipeline):
    """IntegerSerializePipeline

    .. seealso::
        :func:`kim.pipelines.numeric.coerce_to_decimal`
        :func:`kim.pipelines.numeric.to_string`
        :class:`kim.pipelines.serialization.SerializePipeline`
    """

    process_pipes = [coerce_to_decimal, to_string] + SerializePipeline.process_pipes
