from .base import (
    Pipeline, get_data_from_source, update_output_to_name, _decorate_pipe)


def _run_extra_outputs(session, pipe_type):
    for pipe in session.field.opts.extra_serialize_pipes.get(pipe_type, []):
        pipe(session)


def serialize_extra_inputs(session):
    """call list of defined pipes from field.opts.extra_outputs['input']

    .. seealso::
        :func: _run_extra_outputs
    """

    _run_extra_outputs(session, 'input')


def serialize_extra_validators(session):
    """call list of defined pipes from field.opts.extra_outputs['validator']

    .. seealso::
        :func: _run_extra_outputs
    """

    _run_extra_outputs(session, 'validator')


def serialize_extra_processors(session):
    """call list of defined pipes from field.opts.extra_outputs['process']

    .. seealso::
        :func: _run_extra_outputs
    """

    _run_extra_outputs(session, 'process')


def serialize_extra_outputs(session):
    """call list of defined pipes from field.opts.extra_outputs['output']

    .. seealso::
        :func: _run_extra_outputs
    """

    _run_extra_outputs(session, 'output')


class SerializePipeline(Pipeline):
    """SerializePipeline

    .. seealso::
        :func:`kim.pipelines.base.get_data_from_name`
        :func:`kim.pipelines.serialization.serialize_extra_inputs`
        :func:`kim.pipelines.serialization.serialize_extra_processors`
        :func:`kim.pipelines.base.update_output_to_name`
        :func:`kim.pipelines.serialization.serialize_extra_outputs`
    """

    input_pipes = [get_data_from_source, serialize_extra_inputs]
    validation_pipes = []
    process_pipes = [serialize_extra_processors, ]
    output_pipes = [update_output_to_name, serialize_extra_outputs, ]


def validates(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    serialize pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import serialization

        class UserMapper(Mapper):

            name = field.String(required=True)

            @serialization.validates('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'validation', 'serialize', **pipe_opts)

    return wrap


def outputs(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    serialize pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import serialization

        class UserMapper(Mapper):

            name = field.String(required=True)

            @serialization.outputs('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'output', 'serialize', **pipe_opts)

    return wrap


def inputs(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    serialize pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import serialization

        class UserMapper(Mapper):

            name = field.String(required=True)

            @serialization.inputs('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'input', 'serialize', **pipe_opts)

    return wrap


def processes(*fields, **pipe_opts):
    """decorates a method on mapper and its it to the specified fields
    serialize pipeline.

    :params fields: the name of the fields to apply this pipe too
    :params pipe_opts: kwargs passed to newly constructued :class:``Pipe``

    eg::
        from kim.pipelines import serialization

        class UserMapper(Mapper):

            name = field.String(required=True)

            @serialization.processes('name')
            def upper_case(self, session)
                session.data.uppper()
                return session.data
    """

    def wrap(fn):
        return _decorate_pipe(fn, fields, 'process', 'serialize', **pipe_opts)

    return wrap
