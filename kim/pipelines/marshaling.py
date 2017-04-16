from .base import (
    Pipeline, read_only, get_data_from_name, update_output_to_source)


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

    input_pipes = [read_only, get_data_from_name]
    validation_pipes = []
    process_pipes = []
    output_pipes = [update_output_to_source]
