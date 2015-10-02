# kim/pipelines/boolean.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (
    Input, Output,
    marshal_input_pipe, serialize_input_pipe,
    marshal_output_pipe, serialize_output_pipe)


def is_allowed_value(field, data):
    """pipe used to determine is a valid bool value.

    :param field: instance of :py:class:``~.Field`` being pipelined
    :param data: data being piplined for the instance of the field.
    """

    allowed_values = set(field.opts.true_boolean_values
                         + field.opts.false_boolean_values)

    if field.opts.allow_none is True and data is None:
        return data

    if data not in allowed_values:
        raise field.invalid(error_type='type_error')

    return data


def coerce_to_boolean(field, data):
    """Given a valid boolean value, ie True, 'true', 'false', False, 0, 1
    set the data to the python boolean type True or False

    """

    if data is None and field.opts.allow_none:
        return data
    elif data in field.opts.true_boolean_values:
        return True
    else:
        return False


class BooleanInput(Input):

    input_pipes = marshal_input_pipe

    validation_pipes = [
        is_allowed_value,
    ]
    process_pipes = [
        coerce_to_boolean,
    ]
    output_pipes = marshal_output_pipe


class BooleanOutput(Output):

    input_pipes = serialize_input_pipe
    output_pipes = serialize_output_pipe
