# kim/pipelines/nested.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import Input, Output, get_data_from_source, update_output


def marshal_nested(field, data):

    nested_mapper = field.get_mapper(data=data)
    return nested_mapper.marshal(field.opts.role)


def serialize_nested(field, data):

    nested_mapper = field.get_mapper(obj=data)
    return nested_mapper.serialize(field.opts.role)


class NestedInput(Input):

    input_pipes = [
        get_data_from_source,
    ]
    validation_pipes = [
    ]
    process_pipes = [
        marshal_nested
    ]
    output_pipes = [
        update_output,
    ]


class NestedOutput(Output):

    input_pipes = [
        get_data_from_source,
    ]
    process_pipes = [
        serialize_nested
    ]
    output_pipes = [
        update_output,
    ]
