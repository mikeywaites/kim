from .exceptions import ValidationError
from .utils import is_valid_type


class Field(object):
    """Represents a mapping of a field name and `Type` in a `Mapping`

    """

    def __init__(self, *args, **kwargs):
        """Construct a new ``Field`` object

        :param name: The name of this ``Field`` inside of a
            :class:`kim.mapping.Mapping` data structure.

            The name arg may be omitted at contsruction time.  This is to
            allow the lower level ``Field`` object, which maybe useed directly
            with the mapping api to work with the higher level serializer api
            where the name will be set by the
            :class:`kim.serializers.Serializer` meta class.

        :param field_type: The fields type.  Set using a subclass of
            :class:`kim.types.BaseType`.  the field type argument may be passed
            as an instance of `Type` if type requires arguments or may simply
            be passed as a class.

            # specify type with arguments
            Field('id', MyType(foo='bar'))

            # specify with no type arguments.
            Field('id', MyType)

        :param source: Specify the source of this field. ``Field`` may specify
            a seperate name of the property or key to its `name`.
            When serializing kim will use the source attribute to perform a
            lookup on the data passed to field. e.g::

                obj.my_source = 'foo'
                Field('my_field', String, source='my_source')

                # this would generally map to
                {'my_field': 'foo'}

        :param default: specify a default value of this `Field`.  Non required
            fields may specify a default value for a field when no data is
            provided during serialization.

        :param required: specify that data for this field is required when
            marshaling. During validation a fields source_value will be checked
            early on to make sure the field has a value when required.

        :param read_only: specify that this field should only be used when for
            output during serialization and MUST not accept a value during
            marshaling.  By default `Field` will simply ignore data for a read
            only data.

        :param extra_validators: specify an iterable of callable validators
            that will be run along with `field_types` defined validators.

            .. seealso::
                :class:`kim.validators.Validator`

        :param allow_none: Allow the value of `Field` to be None when
            serializing.

        """

        args = list(args)

        name = kwargs.pop('name', None)
        if args:
            if isinstance(args[0], basestring):
                if name is not None:
                    raise Exception(
                        "May not pass name positionally and as a keyword.")
                name = args.pop(0)

        field_type = kwargs.pop('field_type', None)
        if args:
            type_ = args[0]

            if hasattr(type_, '_kim_type'):
                if field_type is not None:
                    raise Exception(
                        "May not pass type_ positionally and as a keyword.")
                field_type = args.pop(0)

        if field_type is None:
            raise Exception('field type must be provided')
        elif not is_valid_type(field_type):
            field_type = field_type()

        self.field_type = field_type
        self.name = name
        self._source = kwargs.pop('source', None)
        self._attr_name = kwargs.pop('attr_name', None)
        self.default = kwargs.pop('default', None)
        self.required = kwargs.pop('required', True)
        self.allow_none = kwargs.pop('allow_none', True)
        self.read_only = kwargs.pop('read_only', False)
        self.extra_validators = kwargs.pop('extra_validators', [])

    @property
    def source(self):
        """
        ``source`` is the attribute name the value of this field will be taken
        from when serializing. When marshaling, source is the name of
        the key that will be set on the resulting dict.

        if _source has no value then source will return ``self.name``

        """
        return self._source or self.name

    @property
    def attr_name(self):
        """
        ``attr_name`` is a unique string identifying this Field.
        This can be passed to a role whitelist/blacklist.
        When instantiated via a Serializer, ``attr_name`` will automatically be
        set to the attribute name of this Field on the serializer class.

        if _attr_name has no value then _attr_name will return ``self.name``

        """
        return self._attr_name or self.name

    def marshal(self, value):
        """Call the :meth:`marshal_value` method of `type` providing the
        ``field_type`` validates.

        :returns: value returned from :meth:`marshal_value`
        """
        if self.is_valid(value):
            return self.field_type.marshal_value(value)

    def serialize_value(self, value):
        """Call the :meth:`serialize_value` method of `type`.

        :returns: value returned from :meth:`serialize_value`
        """
        return self.field_type.serialize_value(value)

    def is_valid(self, value):
        """validates a field against ``value``.  This method handles
        top level validation against field properties such
        as ``read_only`` and ``required``.

        Once field level validation is handled :meth:``field_type.validate``
        will be called.

        :param value: value passed to field for marshaling or serialization.

        :raises: :class:`kim.exceptions.ValidationError`
        :returns: True if all validators run without error.
        """

        # if read only is True, not further validation is needed.
        if self.read_only:
            return True

        if self.required and value is None:
            raise ValidationError("This is a required field")
        elif not self.allow_none and value is None:
            raise ValidationError("This can not be None")

        try:
            self.field_type.validate(value)
        except ValidationError as e:
            raise e

        return True
