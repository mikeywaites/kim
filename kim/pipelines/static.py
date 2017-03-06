# kim/pipelines/static.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import pipe
from .serialization import SerializePipeline


@pipe(run_if_none=True)
def get_static_value(session):
    """return the static value specified in FieldOpts
    """

    session.data = session.field.opts.value

    return session.data


class StaticSerializePipeline(SerializePipeline):
    """StaticSerializePipeline

    .. seealso::
        :func:`kim.pipelines.static.get_static_value`
        :class:`kim.pipelines.serialization.SerializePipeline`
    """

    process_pipes = [get_static_value, ] + SerializePipeline.process_pipes
