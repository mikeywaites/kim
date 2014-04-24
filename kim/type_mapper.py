from .exceptions import ValidationError


class BaseTypeMapper(object):
    """A `TypeMapper` is a Wrapper around kim `Types` used in `Mapping`
    structures.

    e.g:
        mapping = Mapping(TypeMapper('email', String))

        The example above would map a :class:`kim.types.String`
        type to a field called 'email'.

    :param name: The name of the field to marshal to.

    :param type: The `Type` class or a `Type` instance

    :param source: specify attr used in marshaling and serialization

    :param default: for a non required `TypeMapper` allow a default value

    :param required: Specify wether this `TypeMapper` value is required

    .. seealso::
        :class:`kim.types.BaseType`
        :class:`kim.serializers.Serializer`
    """

    def __init__(self, name, type,
                 source=None,
                 extra_validators=None,
                 **options):

        self.type = type
        self.name = name
        self.source = source or name
        self.default = options.pop('default', type.default)
        self.extra_validators = extra_validators or []

    def marshal_value(self, source_value):
        """Call the :meth:`marshal_value` method of `type`.

        :returns: value returned from :meth:`marshal_value`
        """
        return self.type.marshal_value(source_value)

    def serialize_value(self, source_value):
        """Call the :meth:`serialize_value` method of `type`.

        :returns: value returned from :meth:`serialize_value`
        """

        return self.type.serialize_value(source_value)

    def validate(self, source_value):
        result = self.type.validate(source_value)

        for validator in self.extra_validators:
            result = result and validator(source_value)
        return result

    def include_in_serialize(self):
        return self.type.include_in_serialize()

    def include_in_marshal(self):
        return self.type.include_in_marshal()


class TypeMapper(BaseTypeMapper):
    pass