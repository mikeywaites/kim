#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict
from .exceptions import ValidationError


class BaseType(object):

    default = None

    error_message = 'An error ocurred validating this field'

    def get_error_message(self, source_value):
        """Return a valiation error message for this Type

        :returns: an error message explaining the error that occured
        """
        return unicode(self.error_message)

    def marshal_value(self, source_value):
        """:meth:`marshal_value` called during marshaling of data.

        This method provides a hook for types to perform additonal operations
        on the `source_value` being marshalled.

        :returns: `source_value`
        """
        return source_value

    def serialize_value(self, source_value):
        """:meth:`serialize_value` called during serialization of data.

        This method provides a hook for types to perform additonal operations
        on the `source_value` being serialized.

        :returns: `source_value`
        """

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
        :returns: True
        """
        return True

    def validate_for_marshal(self, source_value):
        return self.validate(source_value)

    def validate_for_serialize(self, source_value):
        return self.validate(source_value)


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

        return super(TypedType, self).validate(source_value)


class String(TypedType):

    type_ = basestring

    default = ''


class Integer(TypedType):

    type_ = int

    default = int


class Nested(BaseType):
    """Create a `Nested` mapping from a :class:`kim.mapping.BaseMapping`
    or Mapped :class:`kim.serializers.SerializerABC`

    Nested type allow you to build up reusable mapping structures.  They
    can be used to build up complex structures and also support the use
    of `roles` to allow you to affect the mapped types returned in certain
    use cases.

    e.g::
        food = Mapping(String('type'), String('name'))
        user_mapping = Mapping(String('name'),
                               Nested('foods', food_mapping)

    a Nested type may also specify a role to allow flexibly changing the
    types returned from a nested mapping.  This further increases the
    flexibilty and reusability of mappings.  For example, in certain cases
    when we want to map our food mapping to another mapping, might might not
    always want to return the 'type' field.

    e.g::
        public_food_role = Role('public', 'name')
        food = Mapping(String('type'), String('name'))
        user_mapping = Mapping(String('name'),
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

    def marshal_value(self, source_value):
        """marshal the `mapping` for this nested type

        :param source_value: data to marshal this `Nested` type to

        :returns: marshalled mapping
        """

        #TODO sort out cicular dep's issue
        from .mapping import marshal
        return marshal(self.get_mapping(), source_value)

    def serialize_value(self, source_value):
        """serialize `source_value` for this NestedType's mapping.

        :param source_value: data to serialize this `Nested` type to

        :returns: serialized mapping
        """

        #TODO sort out cicular dep's issue
        from .mapping import serialize
        return serialize(self.get_mapping(), source_value)

    def validate_for_marshal(self, source_value):
        """iterates Nested mapping calling validate for each
        field in the mapping.  Errors from each field will be stored
        and finally raised in a collection of errors

        :raises: ValidationError
        :returns: True
        """

        from .mapping import get_attribute

        errors = defaultdict(list)
        for field in self.get_mapping().fields:
            value = get_attribute(source_value, field.name)
            try:
                field.validate_for_marshal(value)
            except ValidationError as e:
                errors[field.name].append(e.message)

        if errors:
            raise ValidationError(errors)
        else:
            return super(Nested, self).validate_for_marshal(source_value)

    def validate_for_serialize(self, source_value):
        """iterates Nested mapping calling validate for each
        field in the mapping.  Errors from each field will be stored
        and finally raised in a collection of errors

        :raises: ValidationError
        :returns: True
        """

        from .mapping import get_attribute

        errors = defaultdict(list)
        for field in self.get_mapping().fields:
            value = get_attribute(source_value, field.source)
            try:
                field.validate_for_serialize(value)
            except ValidationError as e:
                errors[field.source].append(e.message)

        if errors:
            raise ValidationError(errors)
        else:
            return super(Nested, self).validate_for_serialize(source_value)


class BaseTypeMapper(object):
    """A `TypeMapper` is a Wrapper around kim `Types` used in `Mapping`
    structures.

    e.g:
        mapping = Mapping(TypeMapper('email', String))

        The example above would map a :class:`kim.types.String`
        type to a field called 'email'.

    :param name: The name of the field to marshal to.

    :param base_type: The `Type` class or a `Type` instance

    :param source: specify attr used in marshaling and serialization

    :param default: for a non required `TypeMapper` allow a default value

    :param required: Specify wether this `TypeMapper` value is required

    .. seealso::
        :class:`kim.types.BaseType`
        :class:`kim.serializers.Serializer`
    """

    def __init__(self, name, base_type,
                 source=None,
                 required=True,
                 allow_none=True,
                 **options):

        self.base_type = base_type
        self.name = name
        self.source = source or name
        self.required = required
        self.allow_none = allow_none
        self.default = options.pop('default', base_type.default)

    def marshal_value(self, source_value):
        """Call the :meth:`marshal_value` method of `base_type`.

        :returns: value returned from :meth:`marshal_value`
        """
        return self.base_type.marshal_value(source_value)

    def serialize_value(self, source_value):
        """Call the :meth:`serialize_value` method of `base_type`.

        :returns: value returned from :meth:`serialize_value`
        """

        return self.base_type.serialize_value(source_value)

    def validate(self, source_value):
        """Call :meth:`validate` on `base_type`.

        """
        if self.required and not source_value:
            raise ValidationError("This is a required field")

        elif not self.allow_none and source_value is None:
            raise ValidationError("This field cannot be None")

        else:
            return self.validate_type(source_value)

    def validate_for_marshal(self, source_value):
        return self.validate(source_value)

    def validate_for_serialize(self, source_value):
        return self.validate(source_value)


class TypeMapper(BaseTypeMapper):

    def validate_type(self, source_value):
        """Call :meth:`validate` on `base_type`.

        """
        return self.base_type.validate(source_value)


class Collection(TypedType):

    type_ = list

    default = list()

    def __init__(self, inner_type, *args, **kwargs):
        self.inner_type = inner_type
        if not is_valid_type(self.inner_type):
            raise TypeError("Collection() requires a valid Type "
                            "as its first argument")

        super(Collection, self).__init__(*args, **kwargs)

    def marshal_value(self, source_value):

        return [self.inner_type.marshal_value(member)
                for member in source_value]

    def serialize_value(self, source_value):

        return [self.inner_type.serialize_value(member)
                for member in source_value]

    def validate(self, source_value):
        """Call :meth:`validate` on `base_type`.

        """
        super(Collection, self).validate(source_value)
        return [self.inner_type.validate(mem) for mem in source_value]


def is_valid_type(type_):
    """Validate that `type_` is an instance or subclass of
    :class:`kim.types.BaseType`.

    :rtype: boolean
    :returns: True or False
    """

    return isinstance(type_, BaseType) or issubclass(type_, BaseType)
