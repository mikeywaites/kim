#from .exceptions import MappingError

from .types import TypeABC


class MappingABC(object):
    pass


class Mapping(MappingABC):
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

        Any field inherting from :class:`kim.fields.TypeABC` is considered
        to be a valid field passed into a mapping.

    :param collection: Provided as a keyword arg to a `mapping` sets the data
                       structure used to store `fields` in. (default list)

    .. seealso::

        :class:`kim.fields.TypeABC`

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
            if isinstance(item, TypeABC):
                self.add_field(item)

    def add_field(self, field):
        """Add a `field` type to the `fields` collection.

        :param field: A field type

        .. seealso::
            :class:`kim.fields.TypeABC`

        :returns: None
        """
        self.fields.append(field)
