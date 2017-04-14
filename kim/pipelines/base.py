# kim/pipelines/base.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from itertools import chain
from functools import wraps

from kim.exception import StopPipelineExecution, FieldError
from kim.utils import attr_or_key, set_attr_or_key, attr_or_key_update


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

    Everytime a :class:`kim.field.Field` is marshaled or serialized a session object
    is created for each field that persists across every pipe inside of the fields
    MarsahlingPipeline or SerializationPipeline.

    Each pipe in a pipeline is able to work with the data set by the previous pipe using
    the session object.

    Example::

        from kim.pipelines.base import pipe

        @pipe()
        def odds_evens(session):

            if session.data is not None:
                if session.data % 2:
                    session.data = 'evens'
                else:
                    session.data = 'odds'

    In the example above our pipe changes the data of our pipeline based on the current
    value of session.data.

    As well as providing the interface to the data in a fields pipeline, the Session
    object also provides pipes with access to the overal state of that marshaling or
    serialization pipeline.
    """

    __slots__ = ('field', 'data', 'output', 'parent', 'mapper_session')

    def __init__(self, field=None, data=None, output=None,
                 parent=None, mapper_session=None):
        """Construct a new session.

        :param field: an instance of :class:`kim.field.Field` the scope of this session
            is bound too.
        :param data: data that has been passed along the pipeline field marshaling or
            serialization session.
        :param output: An object that contains the output of this fields marshaling
            or serialization session.
        :param parent:  If this is a wrapped field, then the parent kwarg will be a
            referrence to the instance of the field wrapping field.
        :param mapper_session: The overal mapper marshaling or serialization session
            this field session belongs to.
        """
        self.field = field
        self.data = data
        self.output = output
        self.parent = parent
        self.mapper_session = mapper_session

    @property
    def mapper(self):
        """Return the :class:`kim.mapper.Mapper` bound to the scope of this Session.

        :returns: The :class:`kim.mapper.Mapper` bound to this Session.
        :rtype: :class:`kim.mapper.Mapper`
        """
        return self.mapper_session.mapper


def pipe(**pipe_kwargs):
    """Pipe decorator is provided as a convenience method for creating Pipe
    objects.

    :param run_if_none: Specify wether the pipe function should be called if session.data
        is None.

    Usage::

        from kim.pipelines.base import pipe

        @pipe(run_if_none=True)
        def my_pipe(session):

            do_stuff(session)

    .. seealso::
        :class:`kim.pipelines.base.Pipe`
    """

    def pipe_decorator(pipe_func):

        @wraps(pipe_func)
        def inner(session, *args, **kwargs):

            if session.data is not None:
                return pipe_func(session)
            elif session.data is None and pipe_kwargs.get('run_if_none'):
                return pipe_func(session)
            else:
                return session.data

        return inner

    return pipe_decorator


#TODO(mike) Let's remove this functionality.  The decoarted @validates() methods
# Didn't work as well as planned.
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
    """Pipelines provide a simple, extensible way of processing data for
    a :class:`kim.field.Field`.  Each pipeline provides 4 input groups,
    ``input_pipes``, ``validation_pipes``, ``process_pipes`` and ``output_pipes``.
    Each containing `pipe` functions that are called in order
    passing data from one pipe to another.

    Kim pipes are similar to unix pipes, where each pipe in the chain has a
    single role in handling data before passing it on to the next pipe in the
    chain.

    Pipelines are typically ignorant to whether they
    are marhsaling data or serializing data, they simply take data in one end,
    this may be a deserialized dict of JSON or an object
    that's been populated from the database, and produce an output
    at the other.

    Usage::

        from kim.pipelines.base import Pipeline

        class StringIntPipeline(Pipeline):

            input_pipes = [get_data_from_json]
            validation_pipes = [is_numeric_string]
            process_pipes [cast_to_int]
            output_pipes = [update_output]
    """

    input_pipes = []
    validation_pipes = []
    process_pipes = []
    output_pipes = []

    __slots__ = ()



def run_pipeline(pipeline, mapper_session, field, **opts):
    """ Iterate over all of the defined ``pipes`` for this pipeline.

    :param parent_session: The field being processed by this Pipeline is wrapped,
        parent_session will be passed and set on the fields session.
    :returns: Returns the output of the pipelines session.
    :rtype: mixed
    """
    parent = opts.get('parent_session', None)

    session = Session(
        field, mapper_session.data, mapper_session.output,
        mapper_session=mapper_session,
        parent=parent)

    # chain all the pipelines pipes together and process them until the all the
    # pipe groups have been exhausted or until
    # :class:`kim.exception.StopPipelineExecution` is raised.
    try:
        for pipe_func in chain(pipeline.input_pipes, pipeline.validation_pipes,
                               pipeline.process_pipes, pipeline.output_pipes):
            pipe_func(session)

        return session.output

    except StopPipelineExecution:
        return session.output


@pipe(run_if_none=True)
def get_data_from_name(session):
    """Extracts a specific key from data using ``field.name``.  This pipe is
    typically used as the entry point to a chain of input pipes.

    :param session: Kim pipeline session instance

    :rtype: mixed
    :returns: the key found in data using field.name

    """

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the name.
    if session.field.opts._is_wrapped:
        return session.data

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
    """Extracts a specific key from data using ``field.source``.  This pipe is
    typically used as the entry point to a chain of output pipes.

    :param session: Kim pipeline session instance

    :rtype: mixed
    :returns: the key found in data using field.source

    """

    source = session.field.opts.source

    # If the field is wrapped by another field then the relevant data
    # will have already been pulled from the source.
    if session.field.opts._is_wrapped or source == '__self__':
        return session.data

    value = attr_or_key(session.data, source)
    session.data = value
    return session.data


@pipe(run_if_none=True)
def get_field_if_required(session):

    if session.data is None:
        session.data = session.field.opts.default

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
    """Store ``data`` at ``field[name]`` for a ``field`` inside
    of ``output``

    :param session: Kim pipeline session instance

    :returns: None
    """
    session.output[session.field.name] = session.data


@pipe(run_if_none=True)
def update_output_to_source(session):
    """Store ``data`` at field.opts.source for a ``field`` inside
    of ``output``

    :param session: Kim pipeline session instance

    :raises: FieldError
    :returns: None
    """

    source = session.field.opts.source
    try:
        if source == '__self__':
            attr_or_key_update(session.output, session.data)
        else:
            set_attr_or_key(session.output, session.field.opts.source, session.data)
    except (TypeError, AttributeError):
        raise FieldError('output does not support attribute or '
                         'key based set operations')
