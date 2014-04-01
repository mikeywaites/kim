#!/usr/bin/python
# -*- coding: utf-8 -*-

from .exceptions import ValidationError


class BaseType(object):

    default = None

    error_message = 'An error ocurred validating this field'

    def get_error_message(self, source_value):
        """Return a valiation error message for this Type

        :returns: an error message explaining the error that occured
        """
        return unicode(self.error_message)

    def get_value(self, source_value):
        return source_value

    def validate(self, source_value):
        """Validate the `source_value` is of a valid type. If `source_value`
        is invalid a :class:`kim.exceptions.ValidationError` should be raised

        :param source_value: the value being validated.

        e.g::
            def validate(self, source_value):
                if not isinstance(source_value, str):
                    raise ValidationError("Invalid type")

        :raises: :class:`kim.exceptions.ValidationError`
        :returns: None
        """
        pass


class TypedType(BaseType):

    type_ = None

    error_message = 'This field was of an incorrect type'

    def validate(self, source_value):
        """validates that source_value is of a given type

        .. seealso::
            :meth:`kim.types.BaseType.validate`

        :raises: :class:`kim.exceptions.ValidationError`, TypeError
        :returns: None
        """
        if not isinstance(source_value, self.type_):
            raise ValidationError(self.get_error_message(source_value))


class String(TypedType):

    type_ = basestring

    default = ''


class Integer(BaseType):

    default = int


class Nested(BaseType):
    """Create a `Nested` mapping from a :class:`kim.mapping.BaseMapping`
    or Mapped :class:`kim.serializers.SerializerABC`

    Nested type allow you to build up reusable mapping structures.  They
    can be used to build up complex structures and also support the use
    of `roles` to allow you to affect the mapped types returned in certain
    use cases.

    e.g::
        food = Mapping('food', String('type'), String('name'))
        user_mapping = Mapping('users',
                               String('name'),
                               Nested('foods', food_mapping)

    a Nested type may also specify a role to allow flexibly changing the
    types returned from a nested mapping.  This further increases the
    flexibilty and reusability of mappings.  For example, in certain cases
    when we want to map our food mapping to another mapping, might might not
    always want to return the 'type' field.

    e.g::
        public_food_role = Role('public', 'name')
        food = Mapping('food', String('type'), String('name'))
        user_mapping = Mapping('users',
                               String('name'),
                               Nested('foods', food_mapping,
                                      role=public_food_role)

    In this example that only the `name` field should be included.

    .. seealso::
        :class:`BaseType`

    """

    def __init__(self, mapped=None, role=None, *args, **kwargs):
        """:class:`Nested`

        :param name: name of this `Nested` type
        :param mapped: a :class:`kim.mapping.BaseMapping` or Mapped
                   Serializer instance
        :param role: :class:`kim.roles.RolesABC` role

        .. seealso::
            :class:`BaseType`
        """

        self._mapping = None
        self.mapping = mapped
        self.role = role

        super(Nested, self).__init__(*args, **kwargs)

    @property
    def mapping(self):
        """Getter property to retrieve the mapping for this `Nested` type.

        :returns: self._mapping
        """
        return self._mapping

    @mapping.setter
    def mapping(self, mapped):
        """Setter for mapping property

        the :param:`mapped` arg must be a valid
        :class:`kim.mapping.BaseMapping` or Mapped Serializer instance.

        :raises: TypeError
        """

        #TODO sort out the cicular imports
        from .mapping import BaseMapping

        try:
            self._mapping = mapped.__mapping__
        except AttributeError:
            self._mapping = mapped

        if not isinstance(self._mapping, BaseMapping):
            raise TypeError('Nested() must be called with a '
                            'mapping or a mapped serializer instance')

    def get_mapping(self):
        """Return the mapping defined for this `Nested` type.

        If a `role` has been passed to the `Nested` type the mapping
        will be run through the role automatically

        :returns: :class:`kim.mapping.BaseMapping` type

        .. seealso::
            :class:`kim.roles.Role`
        """
        if self.role:
            return self.role.get_mapping(self.mapping)

        return self.mapping

    def get_value(self, source_value):
        """marshall the `mapping` for this nested type

        :param source_value: data to marshall this `Nested` type to

        :returns: marshalled mapping
        """

        #TODO sort out cicular dep's issue
        from .mapping import serialize
        return serialize(self.get_mapping(), source_value)


class MappedType(object):
    """Wrapper representing a :class:`kim.types.Type` in a
    :class:`kim.serializers.Serializer`.

    :param field_type: The `Type` class to use for this `Field` (note this should
        be a class, not an instantiated object)
    :param **params: Extra params to be passed to the `Type` constructor, eg.
        `source`

    .. seealso::
        :class:`kim.serializers.Serializer`
    """

    def __init__(self, name, base_type, source=None, required=True, default=None):
        self.base_type = base_type
        self.name = name
        self.source = source or name
        self.required = required
        self.default = base_type.default or default

    def get_value(self, source_value):
        return self.base_type.get_value(source_value)

    def validate(self, source_value):
        """Call validate on `base_type`.

        """
        if self.required and not source_value:
            raise ValidationError("This is a required field")

        return self.base_type.validate(source_value)


class MappedCollectionType(MappedType):

    def get_value(self, source_value):
        return [self.base_type.get_value(member) for member in source_value]
