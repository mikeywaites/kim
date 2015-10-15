# kim/pipelines/numeric.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

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
