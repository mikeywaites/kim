# kim/field.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .utils import set_creation_order
from .pipelines import Input, Output, StringInput, StringOutput


class FieldError(Exception):
    pass


class FieldOpts(object):

    def __init__(self, **opts):

        self._opts = opts

        self.required = opts.pop('required', False)
        self.default = opts.pop('default', None)
        self.source = opts.pop('source', None)
        self.attribute_name = opts.pop('attribute_name', None)
        self.name = opts.pop('name', self.attribute_name)
        self.allow_none = opts.pop('allow_none', True)


class Field(object):
    """Field, as its name suggests, represents a single field or 'key' inside
    your mapping.  They instruct kim on how it should pass data in and push
    data out of your objects.

    Fields are somewhat dumb in that they simply act as a wrapper around an
    Input pipeline and an Output pipeline by defining the configuration options
    for each.

    .. code-block:: python

        from kim import Mapper
        from kim import field

        class UserMapper(Mapper):

            id = field.Integer(required=True, read_only=True)
            name = field.String(required=True)
    """

    opts_class = FieldOpts
    input_pipe = Input
    output_pipe = Output

    def __init__(self, **field_opts):
        """Construct a new instance of field.  Each field accepts a set of
        kwargs that will be passed directly to the fields
        defined ``opts_class``.
        """

        self.opts = self.opts_class(**field_opts)

        set_creation_order(self)

    def invalid(self, message):
        """Raise an Exception using the provided ``message``.  This method
        is typically used by pipes to allow :py:class:``~.Field`` to control
        how its errors are handled.

        :param message: A string message used when outputting field errors
        :raises: FieldError
        """

        raise FieldError(message)

    def get_name(self):
        """Get the name of this field from ``Field.opts``.  If no valid
        attribute_name or name is set, raise an error.

        :raises: :py:class:``~.FieldError``
        :rtype: str
        :returns: the name of the field to be used in input/output
        """

        name = self.opts.name
        if not name:
            cn = self.__class__.__name__
            raise FieldError('{0} requires {0}.name or '
                             '{0}.attribute_name.  Please provide a `name` '
                             'or `attribute_name` param to {0}'.format(cn))

        return name

    def marshal(self, data):

        return self.input_pipe().run(self, data)

    def serialize(self, obj):

        return self.output_pipe().run(self, obj)


class String(Field):

    input_pipe = StringInput
    output_pipe = StringOutput
