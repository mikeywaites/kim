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
                 **options):

        self.base_type = base_type
        self.name = name
        self.source = source or name
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

    def validate_for_marshal(self, source_value):
        return self.base_type.validate_for_marshal(source_value)

    def include_in_serialize(self):
        return self.base_type.include_in_serialize()

    def include_in_marshal(self):
        return self.base_type.include_in_marshal()


class TypeMapper(BaseTypeMapper):
    pass