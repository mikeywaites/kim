#from .exceptions import MappingError

from .types import BaseType, MappedType
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
            'my_mapping',
             String('name'),
             Integer('id'),
        )

    The first argument to the Mapping type is the name of this mapping,
    the following arguments may be any mixture of `Field` types.

    :param name: The user defined name of this `mapping`

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
        try:
            mapping_name, args = args[0], args[1:]
        except IndexError:
            raise TypeError("Mapping() takes at least one argument")

        self.name = mapping_name
        self.fields = kwargs.get('collection', list())

        self._arg_loop(args)

    def __iter__(self):
        return iter(self.fields)

    def _arg_loop(self, items):
        """Iterates over collection of constructor args and assigns
        accordingly.

        :param items: collection of Field and Role type args.

        :returns: None
        """

        for item in items:
            if isinstance(item, MappedType):
                self.add_field(item)

    def add_field(self, field):
        """Add a `field` type to the `fields` collection.

        :param field: A field type

        .. seealso::
            :class:`kim.fields.BaseType`

        :returns: None
        """
        self.fields.append(field)


def get_field_data(field, data):
    """Attempt to find the value for a `field` from `data`.

    :param data: dict like object containing input data
    :param field: mapped field.

    :returns: the value for `field` from `data`
    """

    return getattr(data, field.source, None)


def mapping_iterator(mapping, data):
    """iterate over a `mapping` validating `data` for each mapped
    type defined in a `mapping`

    Assuming a field validate, mapping_iterator will yield the field and
    the value for the field pulled from `data`

    :raises: ValidationError
    """

    errors = dict()

    for field in mapping.fields:
        value = get_field_data(field, data)
        try:
            field.validate(value)
        except ValidationError as e:
            errors.setdefault(field.source, [])
            errors[field.source].append(e.message)

        if field.source not in errors:
            yield field, value

    if errors:
        raise ValidationError(errors)


def marshal(mapping, data):
    """`marshall` data to an expected output for a
    `mapping`

    :param mapping: :class:`kim.mapping.Mapping`
    :param data: `dict` or collection of dicts to marshall to a `mapping`

    :raises: TypeError
    :rtype: dict
    :returns: serializable object mapped from `mapping`
    """

    output = {}
    for field, value in mapping_iterator(mapping, data):

        output[field.name] = field.get_value(value)

    return output


def serialize(mapping, data):
    output = {}
    for field, value in mapping_iterator(mapping, data):

        output[field.name] = field.from_value(value)

    return output
