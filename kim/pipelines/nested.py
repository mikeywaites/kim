# kim/pipelines/nested.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .base import Input, Output, get_data_from_source, update_output


def _handle_nested(field, method, data):

    if field.opts.many:
        nested_mapper = field.get_mapper(as_class=True).many()
        return getattr(nested_mapper, method)(data, role=field.opts.role)
    else:
        params = {'data': data} if method == 'marshal' else {'obj': data}
        nested_mapper = field.get_mapper(**params)
        return getattr(nested_mapper, method)(role=field.opts.role)


def marshal_nested(field, data):

    return _handle_nested(field, 'marshal', data)


def serialize_nested(field, data):

    return _handle_nested(field, 'serialize', data)


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
