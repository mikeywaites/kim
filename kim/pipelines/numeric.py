# kim/pipelines/numeric.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import (
    pipe,
    Input, Output, marshal_input_pipe, marshal_output_pipe,
    serialize_input_pipe, serialize_output_pipe)


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


class IntegerInput(Input):

    input_pipes = marshal_input_pipe

    validation_pipes = [
        is_valid_integer
    ]
    output_pipes = marshal_output_pipe


class IntegerOutput(Output):

    input_pipes = serialize_input_pipe
    output_pipes = serialize_output_pipe
