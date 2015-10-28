# kim/pipelines/base.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from itertools import chain
from functools import wraps

from kim.exception import StopPipelineExecution, FieldError
from kim.utils import attr_or_key


class Pipe(object):
    """Base pipe class wrapping a pipe func allowing users to provide
    custom base pipe objects.

    """

    def __init__(self, func=None, run_if_none=False, *args, **kwargs):
        self.func = func
        self.run_if_none = run_if_none

    def __call__(self, session, *args, **kwargs):

        return self.run(session, **kwargs)

    def run(self, session, **kwargs):

        if session.data is not None:
            return self.func(session, **kwargs)
        elif session.data is None and self.run_if_none:
            return self.func(session, **kwargs)
        else:
            return session.data


class Session(object):
    """Pipeline session objects acts as store for the state passed between
    one pipe method to another.

    """

    def __init__(self, field, data, output,
                 partial=False, parent=None, **kwargs):

        self.field = field
        self.data = data
        self.output = output
        self.partial = partial
        self.parent = parent


def pipe(**pipe_kwargs):
    """pipe decorator is provided as a convenience method for creating Pipe
    objects
    """

    def pipe_decorator(pipe_func):

        @wraps(pipe_func)
        def inner(session, *args, **kwargs):

            return Pipe(pipe_func, **pipe_kwargs)(session)

        return inner

    return pipe_decorator


def _decorate_pipe(fn, fields, pipe_type, pipeline_type, **pipe_opts):

    fn.__mapper_field_hook = pipe_type
    fn.__mapper_field_hook_opts = {
        'serialize': pipeline_type == 'serialize',
        'marshal': pipeline_type == 'marshal',
        'pipe_opts': pipe_opts
    }
    fn._field_names = fields

    return fn


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

    def run(self, field, data, output, **opts):
        """ Iterate over all of the defined 'pipes' for this pipeline.

        """
        parent = opts.get('parent_session', None)

        parent_partial = parent.partial if parent else False
        partial = opts.get('partial', parent_partial)

        session = Session(
            field, data, output,
            parent=parent,
            partial=partial)

        try:

            for pipe in chain(self.input_pipes, self.validation_pipes,
                              self.process_pipes, self.output_pipes):
                pipe(session)

            return session.output

        except StopPipelineExecution:
            return session.output


@pipe()
def get_data_from_name(session):
    """extracts a specific key from data using field.name.  This pipe is
    typically used as the entry point to a chain of input pipes.

    :param session: Kim pipeline session instance

    :rtype: mixed
    :returns: the key found in data using field.name

    """

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the name.
    if session.field.opts._is_wrapped:
        return session.data

    if session.partial and session.output:
        value = attr_or_key(session.data, session.field.name)
        if value is None:
            value = attr_or_key(session.output, session.field.name)
    else:
        value = attr_or_key(session.data, session.field.name)

    if value is None:
        if session.field.opts.required and session.field.opts.default is None:
            raise session.field.invalid(error_type='required')
        elif session.field.opts.default is not None:
            session.data = session.field.opts.default
            return session.data
        elif not session.field.opts.allow_none:
            raise session.field.invalid(error_type='none_not_allowed')

    session.data = value
    return session.data


@pipe()
def get_data_from_source(session):
    """extracts a specific key from data using field.source.  This pipe is
    typically used as the entry point to a chain of output pipes.

    :param session: Kim pipeline session instance

    :rtype: mixed
    :returns: the key found in data using field.source

    """

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the source.
    if session.field.opts._is_wrapped:
        return session.data

    value = attr_or_key(session.data, session.field.opts.source)
    session.data = value
    return session.data


@pipe()
def read_only(session):
    """End processing of a pipeline if a Field is marked as read_only.

    :param session: Kim pipeline session instance

    :raises  StopPipelineExecution:
    """

    if session.field.opts.read_only:
        raise StopPipelineExecution('read_only field')

    return session.data


@pipe()
def is_valid_choice(session):
    """End processing of a pipeline if a Field is marked as read_only.

    :param session: Kim pipeline session instance

    :raises  StopPipelineExecution:
    """

    choices = session.field.opts.choices
    if choices is not None and session.data not in choices:
        raise session.field.invalid('invalid_choice')

    return session.data


@pipe(run_if_none=True)
def update_output_to_name(session):
    """Store ``data`` at field.name for a ``field`` inside
    of ``output``

    :param session: Kim pipeline session instance

    :raises: FieldError
    :returns: None
    """
    try:
        setattr(session.output, session.field.name, session.data)
    except AttributeError:
        try:
            session.output[session.field.name] = session.data
        except TypeError:
            raise FieldError('output does not support attribute or '
                             'key based set operations')


@pipe(run_if_none=True)
def update_output_to_source(session):
    """Store ``data`` at field.opts.source for a ``field`` inside
    of ``output``

    :param session: Kim pipeline session instance

    :raises: FieldError
    :returns: None
    """
    try:
        setattr(session.output, session.field.opts.source, session.data)
    except AttributeError:
        try:
            session.output[session.field.opts.source] = session.data
        except TypeError:
            raise FieldError('output does not support attribute or '
                             'key based set operations')



