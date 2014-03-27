#!/usr/bin/python
# -*- coding: utf-8 -*-

""" The `Roles` module provides the core system for creating and using
`Roles` system with KIM.

"""


class RoleABC(object):
    """Role Abstract Base Class.  All `Role` types MUST inherit from this
    class
    """

    def __init__(self, name, *field_names, **kwargs):
        self.name = name
        self.field_names = field_names


class Role(RoleABC):
    """:class:`kim.roles.Role` is a way to affect the `Types`
    used in a Mapping or Mapped Serializer.  They allow users
    to specify custom sets of field names that are permitted
    or disabled for a defined mapping.
    """

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
