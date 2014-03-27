#from .exceptions import MappingError

from .types import TypeABC, String



class Nested(TypeABC):

    def __init__(self, name='', mapped=None,
                 nullable=True, role=None, *args, **kwargs):

        self._mapping = None
        self.mapping = mapped
        self.nullable = True
        self.role = role

        super(Nested, self).__init__(name, *args, **kwargs)

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, mapped):
        from .serializers import SerializerABC
        if isinstance(mapped, Mapping):
            self._mapping = mapped
        elif isinstance(mapped, SerializerABC):
            self._mapping = mapped.__mapping__
        else:
            raise TypeError('Nested() must be called with a '
                            'mapping or a mapped serializer instance')

    def get_fields(self):
        if self.role:
            return self.role.get_mapping(self.mapping).fields

        return self.mapping.fields


class RoleABC(object):

    def __init__(self, name, *field_names, **kwargs):
        self.name = name
        self.field_names = field_names


class Role(RoleABC):

    def __init__(self, name, *field_names, **kwargs):
        super(Role, self).__init__(name, *field_names, **kwargs)
        self.whitelist = kwargs.pop('whitelist', True)

    def membership(self, field_name):
        if self.whitelist:
            return field_name in self.field_names
        else:
            return field_name not in self.field_names

    def get_mapping(self, mapping):

        fields = [field for field in mapping.fields
                  if self.membership(field.name)]

        MappingKlass = mapping.__class__
        return MappingKlass(
            mapping.name,
            *fields
        )


class Mapping(object):
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


if __name__=="__main__":
    other_mapping = Mapping(
        'food',
        String('name'),
        String('name_2'),
    )
    mapping = Mapping(
        'users',
        String('name'),
        Nested('food', other_mapping, role=Role('test', 'name')),
    )
    mapping.fields[1].get_fields()
    print 'foo'
