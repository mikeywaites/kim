# kim/field.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .exception import FieldError, FieldInvalid, FieldOptsError
from .utils import set_creation_order
from .pipelines import (
    Input, Output,
    StringInput, StringOutput,
    IntegerInput, IntegerOutput,
    NestedInput, NestedOutput,
    CollectionInput, CollectionOutput
)

DEFAULT_ERROR_MSGS = {
    'required': 'This is a required field',
    'type_error': 'Invalid type',
    'not_found': '{name} not found'
}


class FieldOpts(object):
    """FieldOpts are used to provide configuration options to :class:`.Field`.
    They are designed to allow users to easily provide custom configuration
    options to :class:`.Field` classes.

    Custom :class:`.FieldOpts` classes are set on :class:`.Field` using the
    ``opts_class`` property.

    .. code-block:: python

        class MyFieldOpts(FieldOpts):

            def __init__(self, **opts):

                self.some_property = opts.get('some_property', None)
                super(MyFieldOpts, self).__init__(**opts)

    .. seealso::
        :class:`.Field`
    """

    def __init__(self, **opts):
        """ Construct a new instance of :class:`FieldOpts`
        and set config options

        :param name: Specify the name of the field for data output
        :param required: This field must be present when marshaling
        :param attribute_name: Specify an alternative attr name for data output
        :param source: Specify the name of the attr to use when accessing data
        :param default: Specify a default value for this field
        :param allow_none: Speficy if this fields value can be None
        :param read_only: Speficy if this field should be ignored when marshaling
        :param error_msgs: a dict of error_type: error messages.

        :raises: :class:`.FieldOptsError`
        :returns: None
        """

        self._opts = opts.copy()

        # set attribute_name, name and source options.
        name = opts.pop('name', None)
        attribute_name = opts.pop('attribute_name', None)
        source = opts.pop('source', None)
        self.set_name(name=name, attribute_name=attribute_name, source=source)

        self.error_msgs = DEFAULT_ERROR_MSGS.copy()
        self.error_msgs.update(opts.pop('error_msgs', {}))

        self.required = opts.pop('required', False)
        self.default = opts.pop('default', None)

        self.allow_none = opts.pop('allow_none', True)
        self.read_only = opts.pop('read_only', False)

        # internal attrs
        self._is_wrapped = opts.pop('_is_wrapped', False)

        self.validate()

    def validate(self):
        """Allow users to perform checks for required config options.  Concrete
        classes should raise :class:`.FieldError` when invalid configuration
        is encountered.

        A slightly contrived example might be requiring all fields to be
        ``read_only=True``

            from kim.field import FieldOpts

            class MyOpts(FieldOpts):

                def validate(self):

                    if self.read_only is True:
                        raise FieldOptsError('Field cannot be read only')


        :raises: `.FieldOptsError`
        :returns: None
        """
        pass

    def set_name(self, name=None, attribute_name=None, source=None):
        """pragmatically set the name properties for a field.

        :param name: value of name property
        :param attribute_name: value of attribute_name property
        :param source: value of source property

        :returns: None
        """
        self.attribute_name = attribute_name
        self.name = name or self.attribute_name
        self.source = source or self.name

    def get_name(self):
        """return the name property set by :meth:`set_name`

        :rtype: str
        :returns: the name of the field to be used in input/output
        """

        return self.name


class Field(object):
    """Field, as it's name suggests, represents a single key or 'field'
    inside of your mappings.  Much like columns in a database or a csv,
    they provide a way to represent different data types when pusing data
    into and out of your Mappers.

    A core concept of Kims architecture is that of Pipelines.
    Every Field makes use both an Input and Output pipeline which afford users
    a great level of flexibility when it comes to handling data.

    Kim provides a collection of default Field implementations,
    for more complex cases extending Field to create new field types
    couldn't be easier.

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

    def __init__(self, *args, **field_opts):
        """Construct a new instance of field.  Each field accepts a set of
        kwargs that will be passed directly to the fields
        defined ``opts_class``.
        """

        try:
            self.opts = self.opts_class(*args, **field_opts)
        except FieldOptsError as e:
            msg = '{0} field has invalid options: {1}' \
                .format(self.__class__.__name__, e.message)
            raise FieldError(msg)

        set_creation_order(self)

    def get_error(self, error_type):
        """Return the error message for an ``error_type``.

        :param error_type: the key of the error found in self.error_msgs
        """

        parse_opts = {
            'name': self.name
        }
        return self.opts.error_msgs[error_type].format(**parse_opts)

    def invalid(self, error_type):
        """Raise an Exception using the provided ``message``.  This method
        is typically used by pipes to allow :py:class:``~.Field`` to control
        how its errors are handled.

        :param message: A string message used when outputting field errors
        :raises: FieldInvalid
        """

        raise FieldInvalid(self.get_error(error_type))

    @property
    def name(self):
        """proxy access to the :py:class:`.FieldOpts` defined for this field.

        :rtype: str
        :returns: The value of get_name from FieldOpts
        :raises: :py:class:`.FieldError`

        .. seealso::
            :meth:`.FieldOpts.get_name`
        """

        field_name = self.opts.get_name()
        if not field_name:
            cn = self.__class__.__name__
            raise FieldError('{0} requires {0}.name or '
                             '{0}.attribute_name.  Please provide a `name` '
                             'or `attribute_name` param to {0}'.format(cn))

        return field_name

    @name.setter
    def name(self, name):
        """proxy setting the name property via :meth:`.FieldOpts.set_name`

        :param name: the value to set against FieldOpts.name
        :returns: None

        .. seealso::
            :meth:`.FieldOpts.set_name`
        """
        self.opts.set_name(name)

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
    """:class:`.String` represents a value that must be valid
    when passed to str()

    .. code-block:: python

        from kim import Mapper
        from kim import field

        class UserMapper(Mapper):
            __type__ = User

            name = field.String(required=True)

    """

    input_pipe = StringInput
    output_pipe = StringOutput


class Integer(Field):
    """:class:`.Integer` represents a value that must be valid
    when passed to int()

    .. code-block:: python

        from kim import Mapper
        from kim import field

        class UserMapper(Mapper):
            __type__ = User

            id = field.Integer(required=True)

    """

    input_pipe = IntegerInput
    output_pipe = IntegerOutput


class NestedFieldOpts(FieldOpts):
    """Custom FieldOpts class that provides additional config options for
    :class:`.Nested`.

    """

    def __init__(self, mapper_or_mapper_name, **kwargs):
        """Construct a new instance of :class:`.NestedFieldOpts`

        :param mapper_or_mapper_name: a required instance of a :class:`Mapper`
            or a valid mapper name
        :param role: specify the name of a role to use on the Nested mapper
        :param collection_class: provide a custom type to be used when
            mapping many nested objects
        :param getter: provide a function taking (field, data) which returns
            the object to be set on this field, or None if it can't find one.
            This is useful where your API accepts simply `{'id': 2}` but you
            want a full object to be set

        """
        self.mapper = mapper_or_mapper_name
        self.role = kwargs.pop('role', '__default__')
        self.collection_class = kwargs.pop('collection_class', list)
        self.getter = kwargs.pop('getter', None)
        super(NestedFieldOpts, self).__init__(**kwargs)


class Nested(Field):
    """:class:`.Nested` represents an object that is represented by another
    mapper.

    .. code-block:: python

        from kim import Mapper
        from kim import field

        class UserMapper(Mapper):
            __type__ = User

            id = field.String()
            user = field.Nested('OtherMapper', required=True)

    .. seealso::

        :py:class:`.NestedFieldOpts`

    """

    opts_class = NestedFieldOpts
    input_pipe = NestedInput
    output_pipe = NestedOutput

    def get_mapper(self, as_class=False, **mapper_params):
        """Retrieve the specified mapper from the Mapper registry.

        :param mapper_params: A dict of kwarg's to pass to the specified
            mappers constructor
        :param as_class: Return the Mapper class object without
            calling the constructor.  This is typically used when nested
            is mapping many objects.

        :rtype: :py:class:`.Mapper`
        :returns: a new instance of the specified mapper
        """

        from .mapper import get_mapper_from_registry

        mapper = get_mapper_from_registry(self.opts.mapper)
        if as_class:
            return mapper

        return mapper(**mapper_params)


class CollectionFieldOpts(FieldOpts):
    """Custom FieldOpts class that provides additional config options for
    :class:`.Collection`.

    """

    def __init__(self, field, **kwargs):
        """Construct a new instance of :class:`.CollectionFieldOpts`

        :param field: specify the field type mpapped inside of this collection.

        """
        self.field = field
        self.field.opts._is_wrapped = True
        super(CollectionFieldOpts, self).__init__(**kwargs)

    def get_name(self):
        """proxy access to the :py:class:`.FieldOpts` defined for
        this collection field.

        :rtype: str
        :returns: The value of get_name from FieldOpts

        """

        return self.field.name

    def validate(self):

        if not isinstance(self.field, Field):
            raise FieldOptsError('Collection requires a valid Field '
                                 'instance as its first argument')


class Collection(Field):
    """:class:`.Collection` represents  collection of other field types,
    typically stored in a list.

    .. code-block:: python

        from kim import Mapper
        from kim import field

        class UserMapper(Mapper):
            __type__ = User

            id = field.String()
            users = field.Collection(field.Nested('OtherMapper', required=True))
            user_ids = field.Collection(field.String())

    .. seealso::

        :py:class:`.CollectionFieldOpts`

    """

    input_pipe = CollectionInput
    output_pipe = CollectionOutput
    opts_class = CollectionFieldOpts
