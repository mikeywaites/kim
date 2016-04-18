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
    """pipe used to determine if a value can be coerced to an int

    :param session: Kim pipeline session instance

    """

    try:
        return int(session.data)
    except TypeError:
        raise session.field.invalid(error_type='type_error')
    except ValueError:
        raise session.field.invalid(error_type='type_error')


class IntegerMarshalPipeline(MarshalPipeline):

    validation_pipes = \
        [is_valid_integer, is_valid_choice] + MarshalPipeline.validation_pipes


class IntegerSerializePipeline(SerializePipeline):
    pass


@pipe()
def is_valid_decimal(session):
    """pipe used to determine if a value can be coerced to a Decimal

    :param session: Kim pipeline session instance

    """
    try:
        return Decimal(session.data)
    except InvalidOperation:
        raise session.field.invalid(error_type='type_error')


@pipe()
def coerce_to_decimal(session):
    decimals = session.field.opts.precision
    precision = Decimal('0.' + '0' * (decimals - 1) + '1')
    session.data = Decimal(session.data).quantize(precision)
    return session.data


class DecimalMarshalPipeline(MarshalPipeline):

    validation_pipes = [is_valid_decimal] + MarshalPipeline.validation_pipes
    process_pipes = [coerce_to_decimal] + MarshalPipeline.process_pipes


@pipe()
def to_string(session):
    if session.data is not None:
        session.data = str(session.data)
        return session.data


class DecimalSerializePipeline(SerializePipeline):

    process_pipes = [coerce_to_decimal, to_string] + SerializePipeline.process_pipes
