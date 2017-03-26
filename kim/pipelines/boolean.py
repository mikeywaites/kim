# kim/pipelines/boolean.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import pipe, is_valid_choice
from .marshaling import MarshalPipeline
from .serialization import SerializePipeline


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


class BooleanMarshalPipeline(MarshalPipeline):
    """BooleanMarshalPipeline

    .. seealso::
        :func:`kim.pipelines.base.is_valid_choice`
        :func:`kim.pipelines.boolean.coerce_to_boolean`
        :class:`kim.pipelines.marshaling.MarshalPipeline`
    """

    validation_pipes = [is_valid_choice, ] + MarshalPipeline.validation_pipes
    process_pipes = [coerce_to_boolean, ] + MarshalPipeline.process_pipes


class BooleanSerializePipeline(SerializePipeline):
    """BooleanSerializePipeline

    .. seealso::
        :class:`kim.pipelines.serialization.SerializePipeline`
    """
    pass
