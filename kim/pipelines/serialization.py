from .base import (
    Pipeline, get_data_from_source, update_output_to_name, _decorate_pipe)


class SerializePipeline(Pipeline):
    """SerializePipeline

    .. seealso::
        :func:`kim.pipelines.base.get_data_from_name`
        :func:`kim.pipelines.serialization.serialize_extra_inputs`
        :func:`kim.pipelines.serialization.serialize_extra_processors`
        :func:`kim.pipelines.base.update_output_to_name`
        :func:`kim.pipelines.serialization.serialize_extra_outputs`
    """

    input_pipes = [get_data_from_source]
    validation_pipes = []
    process_pipes = []
    output_pipes = [update_output_to_name]
