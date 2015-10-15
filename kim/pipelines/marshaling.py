from .base import (
    Pipeline, read_only, get_data_from_name, update_output_to_source)


def _run_extra_inputs(session, pipe_type):
    for pipe in session.field.opts.extra_inputs.get(pipe_type, []):
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

    input_pipes = [read_only, get_data_from_name, marshal_extra_inputs]
    validation_pipes = [marshal_extra_validators, ]
    process_pipes = [marshal_extra_processors, ]
    output_pipes = [update_output_to_source, marshal_extra_outputs]
