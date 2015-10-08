# kim/pipelines/boolean.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (
    pipe,
    Input, Output,
    is_valid_choice,
    marshal_input_pipe, serialize_input_pipe,
    marshal_output_pipe, serialize_output_pipe)


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
        is_valid_choice,
    ]
    process_pipes = [
        coerce_to_boolean,
    ]
    output_pipes = marshal_output_pipe


class BooleanOutput(Output):

    input_pipes = serialize_input_pipe
    output_pipes = serialize_output_pipe
