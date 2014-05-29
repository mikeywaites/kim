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

        self.name = name
        self.field_type = field_type

        self.field_type = field_type
        self.name = name
        self.source = kwargs.pop('source', name)
        self.attr_name = kwargs.pop('attr_name', name)
        self.default = kwargs.pop('default', None)
        self.required = kwargs.pop('required', True)
        self.allow_none = kwargs.pop('allow_none', True)
        self.read_only = kwargs.pop('read_only', False)
        self.extra_validators = kwargs.pop('extra_validators', [])

    def marshal_value(self, source_value):
        """Call the :meth:`marshal_value` method of `type`.

        :returns: value returned from :meth:`marshal_value`
        """
        try:
            return self.field_type.marshal_value(source_value)
        except TypeError as e:
            raise e

    def serialize_value(self, source_value):
        """Call the :meth:`serialize_value` method of `type`.

        :returns: value returned from :meth:`serialize_value`
        """

        return self.field_type.serialize_value(source_value)

    def validate(self, source):
        """validates a field against ``source_value``.

        :param source_value: a value that this field type should validate
            against.

        :raises: :class:`kim.exceptions.ValidationError`
        :returns: True if all validators run without error.
        """

        try:
            self.field_type.validate(source)
        except ValidationError as e:
            raise e

        return True
