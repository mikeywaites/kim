# kim/pipelines/boolean.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (
    pipe,
    Input, Output,
    marshal_input_pipe, serialize_input_pipe,
    marshal_output_pipe, serialize_output_pipe)


@pipe()
def is_allowed_value(session):
    """pipe used to determine is a valid bool value.

    :param session: Kim pipeline session instance
    """

    allowed_values = set(session.field.opts.true_boolean_values
                         + session.field.opts.false_boolean_values)

    if session.data not in allowed_values:
        raise session.field.invalid(error_type='type_error')

    return session.data


@pipe()
def coerce_to_boolean(session):
    """Given a valid boolean value, ie True, 'true', 'false', False, 0, 1
    set the data to the python boolean type True or False

    :param session: Kim pipeline session instance

    """
    if session.data in session.field.opts.true_boolean_values:
        session.data = True
    else:
        session.data = False

    return session.data


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
