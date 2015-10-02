# kim/pipelines/base.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from functools import wraps

from kim.exception import StopPipelineExecution, FieldError
from kim.utils import attr_or_key


class Pipe(object):

    def __init__(self, func, field, data, output, *args, **kwargs):
        self.func = func
        self.field = field
        self.data = data
        self.output = output

    def run(self):

        return self.func(self.field, self.data)


class OutputPipe(Pipe):

    def run(self):

        return self.func(self.field, self.data, self.output)


def pipe(run_if_none=False, pipe_class=Pipe):

    def pipe_decorator(pipe_func):

        @wraps(pipe_func)
        def inner(field=None, data=None, output=None, *args, **kwargs):

            kwargs.pop('output', {})
            return pipe_class(pipe_func, field, data, output).run()

        return inner

    return pipe_decorator


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
        try:

            for pipe in self.input_pipes:
                pipe_data = pipe(field, pipe_data)

            # validation pipes should not affect the data being piped
            # they only raise exceptions if validation fails.
            for pipe in self.validation_pipes:
                pipe(field, pipe_data)

            for pipe in self.process_pipes:
                pipe_data = pipe(field, pipe_data)

            for pipe in self.output_pipes:
                pipe_data = pipe(field, pipe_data, output)

            return output

        except StopPipelineExecution:
            return output


class Input(Pipeline):
    pass


class Output(Pipeline):
    pass


@pipe()
def get_data_from_name(field, data):
    """extracts a specific key from data using field.name.  This pipe is
    typically used as the entry point to a chain of input pipes.

    :param field: the current instance of :py:class:``~.Field`` being iterated
    :param data: full data object being piped in or out for this ``field``

    :rtype: mixed
    :returns: the key found in data using field.name

    """

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the name.
    if field.opts._is_wrapped:
        return data

    value = attr_or_key(data, field.name)
    if value is None:
        if field.opts.required and field.opts.default is None:
            raise field.invalid(error_type='required')
        elif field.opts.default is not None:
            return field.opts.default
        elif not field.opts.allow_none:
            raise field.invalid(error_type='none_not_allowed')

    return value


@pipe()
def get_data_from_source(field, data):
    """extracts a specific key from data using field.source.  This pipe is
    typically used as the entry point to a chain of output pipes.

    :param field: the current instance of :py:class:``~.Field`` being iterated
    :param data: full data object being piped in or out for this ``field``

    :rtype: mixed
    :returns: the key found in data using field.source

    """

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the source.
    if field.opts._is_wrapped:
        return data

    value = attr_or_key(data, field.opts.source)
    return value


@pipe()
def read_only(field, data):
    """End processing of a pipeline if a Field is marked as read_only.

    :raises  StopPipelineExecution:
    """

    if field.opts.read_only:
        raise StopPipelineExecution('read_only field')

    return data


@pipe(pipe_class=OutputPipe)
def update_output_to_name(field, data, output):
    """Store ``data`` at field.name for a ``field`` inside
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
            raise FieldError('output does not support attribute or '
                             'key based set operations')


@pipe(pipe_class=OutputPipe)
def update_output_to_source(field, data, output=None):
    """Store ``data`` at field.opts.source for a ``field`` inside
    of ``output``

    :param field: instance of :class:`kim.field.Field`
    :param data: the desired value to store in output for the field.
    :param output: and object that supports setattr or key based ops

    :raises: FieldError
    :returns: None
    """
    try:
        setattr(output, field.opts.source, data)
    except AttributeError:
        try:
            output[field.opts.source] = data
        except TypeError:
            raise FieldError('output does not support attribute or '
                             'key based set operations')


marshal_input_pipe = [read_only, get_data_from_name]
serialize_input_pipe = [get_data_from_source, ]
marshal_output_pipe = [update_output_to_source, ]
serialize_output_pipe = [update_output_to_name, ]
