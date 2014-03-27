#!/usr/bin/python
# -*- coding: utf-8 -*-


class TypeABC(object):

    def __init__(self, name, source=None):
        self.name = name
        self.source = source or name

    def get_value(self, source_value):
        return source_value


class String(TypeABC):
    pass


class Integer(TypeABC):
    pass


class Nested(TypeABC):
    """Create a `Nested` mapping from a :class:`kim.mapping.MappingABC`
    or Mapped :class:`kim.serializers.SerializerABC`

    Nested type allow you to build up reusable mapping structures.  They
    can be used to build up complex structures and also support the use
    of `roles` to allow you to affect the mapped types returned in certain
    use cases.

    e.g::
        food = Mapping('food', String('type'), String('name'))
        user_mapping = Mapping('users',
                               String('name'),
                               Nested('foods', food_mapping)

    a Nested type may also specify a role to allow flexibly changing the
    types returned from a nested mapping.  This further increases the
    flexibilty and reusability of mappings.  For example, in certain cases
    when we want to map our food mapping to another mapping, might might not
    always want to return the 'type' field.

    e.g::
        public_food_role = Role('public', 'name')
        food = Mapping('food', String('type'), String('name'))
        user_mapping = Mapping('users',
                               String('name'),
                               Nested('foods', food_mapping,
                                      role=public_food_role)

    In this example that only the `name` field should be included.

    .. seealso::
        :class:`TypeABC`

    """

    def __init__(self, name, mapped=None, role=None, *args, **kwargs):
        """:class:`Nested`

        :param name: name of this `Nested` type
        :param mapped: a :class:`kim.mapping.MappingABC` or Mapped
                   Serializer instance
        :param role: :class:`kim.roles.RolesABC` role

        .. seealso::
            :class:`TypeABC`
        """

        self._mapping = None
        self.mapping = mapped
        self.role = role

        super(Nested, self).__init__(name, *args, **kwargs)

    @property
    def mapping(self):
        """Getter property to retrieve the mapping for this `Nested` type.

        :returns: self._mapping
        """
        return self._mapping

    @mapping.setter
    def mapping(self, mapped):
        """Setter for mapping property

        the :param:`mapped` arg must be a valid
        :class:`kim.mapping.MappingABC` or Mapped Serializer instance.

        :raises: TypeError
        """

        #TODO sort out the cicular imports
        from .serializers import Serializer
        from .mapping import MappingABC

        if isinstance(mapped, MappingABC):
            self._mapping = mapped
        elif isinstance(mapped, Serializer):
            self._mapping = mapped.__mapping__
        else:
            raise TypeError('Nested() must be called with a '
                            'mapping or a mapped serializer instance')

    def get_mapping(self):
        """Return the mapping defined for this `Nested` type.

        If a `role` has been passed to the `Nested` type the mapping
        will be run through the role automatically

        :returns: :class:`kim.mapping.MappingABC` type

        .. seealso::
            :class:`kim.roles.Role`
        """
        if self.role:
            return self.role.get_mapping(self.mapping)

        return self.mapping

    def get_value(self, source_value):
        """marshall the `mapping` for this nested type

        :param source_value: data to marshall this `Nested` type to

        :returns: marshalled mapping
        """

        #TODO sort out cicular dep's issue
        from .mapping import marshal
        return marshal(self.get_mapping(), source_value)
