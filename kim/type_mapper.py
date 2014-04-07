from .exceptions import ValidationError


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

    def validate_helper(self, source_value):
        if self.required and not source_value:
            raise ValidationError("This is a required field")
        elif not self.allow_none and source_value is None:
            raise ValidationError("This field cannot be None")
        elif self.allow_none and source_value is None:
            return True
        # If we get here and None is returned, then we'll delegate to the
        # judgement of the validate_type_for_marshal/serialize

    def validate_for_marshal(self, source_value):
        # First see if validate_helper can give us a definite answer, if not
        # (ie it returns None) then delegate to the base type
        return self.validate_helper(source_value) or self.validate_type_for_marshal(source_value)

    def validate_for_serialize(self, source_value):
        # First see if validate_helper can give us a definite answer, if not
        # (ie it returns None) then delegate to the base type
        return self.validate_helper(source_value) or self.validate_type_for_serialize(source_value)


class TypeMapper(BaseTypeMapper):

    def validate_type_for_marshal(self, source_value):
        """Call :meth:`validate` on `base_type`.

        """
        return self.base_type.validate_for_marshal(source_value)

    def validate_type_for_serialize(self, source_value):
        """Call :meth:`validate` on `base_type`.

        """
        return self.base_type.validate_for_serialize(source_value)
