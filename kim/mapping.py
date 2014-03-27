#from .exceptions import MappingError


class FieldABC(object):

    def __init__(self, name='', source=''):
        self.name = name
        self.source = source


class String(FieldABC):
    pass


class Integer(FieldABC):
    pass


class RoleABC(object):

    def __init__(self, name='', *fields):
        self.name = name
        self.fields = [].extend(fields)


class Role(RoleABC):
    pass


class Mapping(object):
    """:class:`kim.mapping.Mapping` is a factory for generating data
    structures in KIM.

    A mapping consists of a collection of kim `field` interfaces and
    roles.

    `Mappings` are created by passing `Fields` and `Roles`
    to the contructor of :class:`kim.mapping.Mapping`

     e.g.::

        my_mapping = Mapping(
            'my_mapping',
             String('name'),
             Integer('id'),
             Role('overview', 'name', 'id')
        )

    The first argument to the Mapping type is the name of this mapping,
    the following arguments may be any mixture of `Field` and `Role`
    types

    :param name: The user defined name of this `mapping`

    :param fields: contains the `collection` of Field types provided

        Any field inherting from :class:`kim.fields.FieldABC` is considered
        to be a valid field passed into a mapping.

    :param collection: Provided as a keyword arg to a `mapping` sets the data
                       structure used to store `fields` in. (default list)

    .. seealso::

        :class:`kim.fields.FieldABC`
        :class:`kim.roles.RoleABC`

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
        self.roles = {}

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
            if isinstance(item, FieldABC):
                self.add_field(item)

            if isinstance(item, RoleABC):
                self.add_role(item)

    def add_role(self, role):
        """Adds a role to the roles dict keyed by `role.name`: `role`

        :param role: a `Role` type

        .. seealso::
            :class:`kim.roles.RoleABC`

        :returns: None
        """
        self.roles.update({role.name: role})

    def add_field(self, field):
        """Add a `field` type to the `fields` collection.

        :param field: A field type

        .. seealso::
            :class:`kim.fields.FieldABC`

        :returns: None
        """
        self.fields.append(field)
