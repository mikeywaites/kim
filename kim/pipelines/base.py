# kim/pipelines/base.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.utils import attr_or_key


def _run_pipeline(pipes, field, data):
    _data = data
    for func in pipes:

        _data = func(field, _data)

    return _data


class Pipeline(object):

    pipes = []

    def run(self, field, data):

        return _run_pipeline(self.pipes, field, data)


class Input(Pipeline):
    pass


class Output(Pipeline):
    pass


def get_data_from_source(field, data):
    """extracts a specific key from data using field.name.  This pipe is
    typically used as the entry point to a chain of pipes.

    :param field: the current instance of :py:class:``~.Field`` being iterated
    :param data: full data object being piped in or out for this ``field``

    :rtype: mixed
    :returns: the key found in data using field.name

    """

    value = attr_or_key(data, field.get_name())
    if value:
        return value
    elif field.opts.required and not value:
        raise field.invalid('This is a required field')
    elif not value and not field.opts.default and not field.opts.allow_none:
        raise field.invalid('This field cannot be NULL')
    elif not value:
        return field.opts.default
