# kim/field.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .utils import set_creation_order
from .pipelines import (
    Input, Output,
    StringInput, StringOutput,
    IntegerInput, IntegerOutput
)


class FieldError(Exception):
    pass


class FieldOpts(object):

    def __init__(self, _field=None, **opts):

        self._field = _field
        self._opts = opts

        # set attribute_name, name and source options.
        name = opts.pop('name', None)
        attribute_name = opts.pop('attribute_name', None)
        source = opts.pop('source', None)
        self.set_name(name=name, attribute_name=attribute_name, source=source)

        self.required = opts.pop('required', False)
        self.default = opts.pop('default', None)

        self.allow_none = opts.pop('allow_none', True)

    def set_name(self, name=None, attribute_name=None, source=None):
        """pragmatically set the name properties for a field.
        """
        self.attribute_name = attribute_name
        self.name = name or self.attribute_name
        self.source = source or self.name

    def get_name(self):
        """Get the name of this field from ``Field.opts``.  If no valid
        attribute_name or name is set, raise an error.

        :raises: :py:class:``~.FieldError``
        :rtype: str
        :returns: the name of the field to be used in input/output
        """

        name = self.name
        if not name:
            cn = str(self._field)
            raise FieldError('{0} requires {0}.name or '
                             '{0}.attribute_name.  Please provide a `name` '
                             'or `attribute_name` param to {0}'.format(cn))

        return name


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

        self.opts = self.opts_class(_field=self, **field_opts)

        set_creation_order(self)

    def invalid(self, message):
        """Raise an Exception using the provided ``message``.  This method
        is typically used by pipes to allow :py:class:``~.Field`` to control
        how its errors are handled.

        :param message: A string message used when outputting field errors
        :raises: FieldError
        """

        raise FieldError(message)

    @property
    def name(self):
        """proxy access to the :py:class:`.FieldOpts` defined for this field.

        .. seealso::
            :meth:`.FieldOpts.get_name`
        """

        return self.opts.get_name()

    @name.setter
    def name(self, name):
        """proxy setting the name property via :meth:`.FieldOpts.set_name`

        .. seealso::
            :meth:`.FieldOpts.set_name`
        """

        return self.opts.set_name(name)

    def marshal(self, data, output):
        """Run the input pipeline for this field for the given `data` and
        update `output` in place.

        :param data: the full data object the field should be run against
        :param output: the full object the field should output to, in place
        :returns: None
        """

        self.input_pipe().run(self, data, output)

    def serialize(self, obj, output):
        """Run the output pipeline for this field for the given `data` and
        update `output` in place.

        :param data: the full data object the field should be run against
        :param output: the full object the field should output to, in place
        :returns: None
        """

        self.output_pipe().run(self, obj, output)


class String(Field):

    input_pipe = StringInput
    output_pipe = StringOutput


class Integer(Field):

    input_pipe = IntegerInput
    output_pipe = IntegerOutput
