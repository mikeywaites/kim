from .base import (
    Pipeline, read_only, get_data_from_name, update_output_to_source,
    _decorate_pipe)


def _run_extra_inputs(session, pipe_type):
    for pipe in session.field.opts.extra_marshal_pipes.get(pipe_type, []):
        pipe(session)


def marshal_extra_inputs(session):
    """call list of defined pipes from field.opts.extra_inputs['input']

    .. seealso::
        :func: _run_extra_inputs
    """

    _run_extra_inputs(session, 'input')


def marshal_extra_validators(session):
    """call list of defined pipes from field.opts.extra_inputs['validator']

    .. seealso::
        :func: _run_extra_inputs
    """

    _run_extra_inputs(session, 'validation')


def marshal_extra_processors(session):
    """call list of defined pipes from field.opts.extra_inputs['process']

    .. seealso::
        :func: _run_extra_inputs
    """

    _run_extra_inputs(session, 'process')


def marshal_extra_outputs(session):
    """call list of defined pipes from field.opts.extra_inputs['output']

    .. seealso::
        :func: _run_extra_inputs
    """

    _run_extra_inputs(session, 'output')


class MarshalPipeline(Pipeline):
    """MarshalPipeline

    .. seealso::
        :func:`kim.pipelines.base.read_only`
        :func:`kim.pipelines.base.get_data_from_name`
        :func:`kim.pipelines.marsaling.marshal_extra_inputs`
        :func:`kim.pipelines.marshaling.marshal_extra_validators`
        :func:`kim.pipelines.marshaling.marshal_extra_processors`
        :func:`kim.pipelines.base.update_output_to_source`
        :func:`kim.pipelines.marshaling.marshal_extra_outputs`
    """

    input_pipes = [read_only, get_data_from_name, marshal_extra_inputs]
    validation_pipes = [marshal_extra_validators, ]
    process_pipes = [marshal_extra_processors, ]
    output_pipes = [update_output_to_source, marshal_extra_outputs]


def validates(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    marshal pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import marshalling

        class UserMapper(Mapper):

            name = field.String(required=True)

            @marshalling.validates('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'validation', 'marshal', **pipe_opts)

    return wrap


def outputs(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    marshal pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import marshalling

        class UserMapper(Mapper):

            name = field.String(required=True)

            @marshalling.outputs('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'output', 'marshal', **pipe_opts)

    return wrap


def inputs(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    marshal pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import marshalling

        class UserMapper(Mapper):

            name = field.String(required=True)

            @marshalling.inputs('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'input', 'marshal', **pipe_opts)

    return wrap


def processes(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    marshal pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import marshalling

        class UserMapper(Mapper):

            name = field.String(required=True)

            @marshalling.processes('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'process', 'marshal', **pipe_opts)

    return wrap
