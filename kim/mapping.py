#from .exceptions import MappingError

from collections import defaultdict

from .types import BaseTypeMapper
from .exceptions import ValidationError


class BaseMapping(object):
    pass


class Mapping(BaseMapping):
    """:class:`kim.mapping.Mapping` is a factory for generating data
    structures in KIM.

    A mapping consists of a collection of kim `field` types.

    `Mappings` are created by passing `Fields` to the
    contructor of :class:`kim.mapping.Mapping`

     e.g.::

        my_mapping = Mapping(
             String('name'),
             Integer('id'),
        )

    The first argument to the Mapping type is the name of this mapping,
    the following arguments may be any mixture of `Field` types.

    :param fields: contains the `collection` of Field types provided

        Any field inherting from :class:`kim.fields.BaseType` is considered
        to be a valid field passed into a mapping.

    :param collection: Provided as a keyword arg to a `mapping` sets the data
                       structure used to store `fields` in. (default list)

    .. seealso::

        :class:`kim.fields.BaseType`

    """

    def __init__(self, *args, **kwargs):
        """:class:`kim.mapping.Mapping` constructor.

        """
        mapped_types = args[0:]

        self.fields = kwargs.get('collection', list())

        self._arg_loop(mapped_types)

    def __iter__(self):
        return iter(self.fields)

    def _arg_loop(self, items):
        """Iterates over collection of constructor args and assigns
        accordingly.

        :param items: collection of Field and Role type args.

        :returns: None
        """

        for item in items:
            if isinstance(item, BaseTypeMapper):
                self.add_field(item)

    def add_field(self, field):
        """Add a `field` type to the `fields` collection.

        :param field: A field type

        .. seealso::
            :class:`kim.fields.BaseType`

        :returns: None
        """
        self.fields.append(field)


def get_attribute(data, attr, default=None):
    """Attempt to find the value for a `field` from `data`.

    :param data: dict like object containing input data
    :param field: mapped field.

    :returns: the value for `field` from `data`
    """
    if attr == '__self__':
        return data
    elif isinstance(data, dict):
        return data.get(attr, default)
    else:
        return getattr(data, attr, default)


def marshal(mapping, data):
    """`marshal` data to an expected output for a
    `mapping`

    :param mapping: :class:`kim.mapping.Mapping`
    :param data: `dict` or collection of dicts to marshal to a `mapping`

    :raises: TypeError, ValidationError
    :rtype: dict
    :returns: serializable object mapped from `mapping`
    """

    output = {}
    errors = defaultdict(list)

    for field in mapping.fields:
        value = get_attribute(data, field.name)
        try:
            field.validate_for_marshal(value)
        except ValidationError as e:
            errors[field.name].append(e.message)

        if field.name not in errors and not value:
            value = field.default

        if field.source == '__self__':
            output.update(field.marshal_value(value))
        else:
            output[field.source] = field.marshal_value(value)

    if errors:
        raise ValidationError(errors)

    return output


def serialize(mapping, data):
    """Serialize data to an expected input for a `mapping`

    """
    output = {}
    errors = defaultdict(list)

    for field in mapping.fields:
        value = get_attribute(data, field.source)
        try:
            field.validate_for_serialize(value)
        except ValidationError as e:
            errors[field.source].append(e.message)

        if field.source not in errors and not value:
            value = field.default

        output[field.name] = field.serialize_value(value)

    if errors:
        raise ValidationError(errors)

    return output


def marshall_field(field, value):

    # This sucks, not sure what to do here. does marshal handle read only
    # diff to serialize
    if field.read_only:
        return None

    try:
        field.validate_for_marshal(value)
    except FieldError:
        raise

    return field.marshall_value(value or field.default)


class mapping_iterator(object):

    def __init__(self, output=None, errors=None):
        self.output = output or dict()
        self.errors = errors or defaultdict(list)

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):

            try:
                mapping, data = args[0], args[1]
            except IndexError as e:
                # re-reraise a kim error here.
                raise e

            output = self.output
            errors = self.errors
            for field in mapping.fields:
                try:
                    key, value = f(field, data, **kwargs)
                except FieldError as e:
                    errors[e.key].append(e.message)

            return output

        return wrapped_f


@mapping_iterator()
def marshal_v2(field, data):
    """`marshal` data to an expected output for a
    `mapping`

    :param mapping: :class:`kim.mapping.Mapping`
    :param data: `dict` or collection of dicts to marshal to a `mapping`

    :raises: TypeError, ValidationError
    :rtype: dict
    :returns: serializable object mapped from `mapping`
    """

    value = get_attribute(data, field.source)
    return field.source, marshall_field(field, value)


def marshal_sqa_model(mapping, data, instance):

    output = marshal_v2(mapping, data)
    for key, value in output.iteritems():
        setattr(instance, key, value)

    return instance
