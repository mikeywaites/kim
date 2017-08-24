from .base import (
    Pipeline, get_data_from_source, update_output_to_name, set_default)


class SerializePipeline(Pipeline):
    """SerializePipeline

    .. seealso::
        :func:`kim.pipelines.base.get_data_from_name`
        :func:`kim.pipelines.base.update_output_to_name`
    """

    input_pipes = [get_data_from_source]
    validation_pipes = []
    process_pipes = [set_default]
    output_pipes = [update_output_to_name]
