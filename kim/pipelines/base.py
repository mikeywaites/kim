# kim/pipelines/base.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.utils import attr_or_key


class Pipeline(object):
    """Pipelines provide a simple, extensible way of processing data.  Each
    pipeline provides 4 input groups, ``input_pipes``, ``validation_pipes``,
    ``process_pipes`` and ``output_pipes``, each containing `pipe` function
    that are called in order passing data from one pipe to another.

    The idea here is to almost act like pipes in unix,
    where each pipe in the chain has a single role in handling data
    before passing it on to the next pipe in the chain.

    Pipelines are typically ignorant to whether they
    are marhsaling data or serializing data, they simply take data in one end,
    this may be a deserialized dict of JSON or an object
    that's been populated from the database, and produce an output
    at the other.

    """

    input_pipes = []
    validation_pipes = []
    process_pipes = []
    output_pipes = []

    def run(self, field, data, output):
        """ Iterate over all of the defined 'pipes' for this pipeline.

        """
        pipe_data = data
        for pipe in self.input_pipes:
            pipe_data = pipe(field, pipe_data)

        # validation pipes should not affect the data being piped
        # they only raise exceptions of validation fails.
        for pipe in self.validation_pipes:
            pipe(field, pipe_data)

        for pipe in self.process_pipes:
            pipe_data = pipe(field, pipe_data)

        for pipe in self.output_pipes:
            pipe(field, pipe_data, output)

        return output


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

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the source.
    if field.opts._is_wrapped:
        return data

    value = attr_or_key(data, field.name)
    if value:
        return value
    elif field.opts.required and not value:
        raise field.invalid('This is a required field')
    elif not value and not field.opts.default and not field.opts.allow_none:
        raise field.invalid('This field cannot be NULL')
    elif not value:
        return field.opts.default


def update_output(field, data, output):
    """Store ``data`` at the given key or attribute for a ``field`` inside
    of ``output``

    :param field: instance of :class:`kim.field.Field`
    :param data: the desired value to store in output for the field.
    :param output: and object that supports setattr or key based ops

    :raises: FieldError
    :returns: None
    """
    try:
        setattr(output, field.name, data)
    except AttributeError:
        try:
            output[field.name] = data
        except TypeError:
            raise field.invalid('output does not support attribute or '
                                'key based set operations')
