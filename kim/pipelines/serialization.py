from .base import Pipeline, get_data_from_source, update_output_to_name


def _run_extra_outputs(session, pipe_type):
    for pipe in session.field.opts.extra_outputs.get(pipe_type, []):
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

    input_pipes = [get_data_from_source, serialize_extra_inputs]
    validation_pipes = []
    process_pipes = [serialize_extra_processors, ]
    output_pipes = [update_output_to_name, serialize_extra_outputs, ]
