#!/usr/bin/python
# -*- coding: utf-8 -*-

""" The `Roles` module provides the core system for creating and using
the `Roles` system with KIM.

"""


class BaseRole(object):
    """Role Abstract Base Class.  All `Role` types MUST inherit from this
    base class.
    """
    pass


class Role(BaseRole):
    """:class:`kim.roles.Role` is a way to affect the `Types`
    used in a Mapping or Mapped Serializer.  They allow users
    to specify custom sets of field names that are permitted
    or disabled for a defined mapping.

    :param name: The name given to this Role e.g::
        Role('my_role')

    :param field_names: The field names for this role.  Any number of field
    names may be specified as positional arguments
    to the :class:`Role` constructor e.g::
        Role('my_role', 'field_1', 'field_2)

    :param whitelist: Specify wether the `field_names` defined should be allowed
    or disabled for this role. (see :meth:`membership`)
    """

    def __init__(self, *args, **kwargs):
        self.field_names = args
        self.whitelist = kwargs.pop('whitelist', True)

    def membership(self, field_name):
        """Returns a boolean indicating the membership for `field_name`
        in this `role`

        For whitelisted Roles, the :meth:`membership` will check to see
        if `field_name` is defined in `self.field_names`. For blacklisted
        (whitelist=False) the inverse is checked

        This method may be overriden to provide more complex membership
        tests if required.

        e.g::
            >>>role = Role('my_role', 'name', 'email')
            >>>role.membership('foo')
            >>>False

        :rtype: bool
        :returns: True if the field_name is permitted in this role.
        """
        if self.whitelist:
            return field_name in self.field_names
        else:
            return field_name not in self.field_names

    def get_mapping(self, mapping):
        """Creates a new mapping based on this role.

        :param mapping: a :class:`kim.mapping.BaseMapping` mapping type.

        :rtype: :class:`kim.mapping.BaseMapping`
        :returns: a new mapping from this role

        .. seealso::
            :func:`create_mapping_from_role`
        """

        return create_mapping_from_role(self, mapping)


def create_mapping_from_role(role, mapping):
    """utility method that creates a new mapping from `mapping`
    pulling in the allowed fields defined in `role.field_names`

    :param role: :class:`BaseRole` type
    :param mapping: :class:`kim.mapping.BaseMapping` type

    :rtype: :class:`kim.mapping.BaseMapping`
    :returns: New mapping constructred from role.field_names
    """
    fields = [field for field in mapping.fields
              if role.membership(field.name)]

    # We create a new class here from mapping to allow custom mappers
    # TODO what other args, kwargs can a mapping have?
    MappingKlass = mapping.__class__
    return MappingKlass(
        *fields
    )


def _create_role(fields, role_base=None, whitelist=True, **kwargs):
    """Factory function for generating new Roles derived from an
    optional custom role class

    :param name: the name given to this role
    :param fields: iterable of field names
    :param role_base: specify a custom role type to create a role from
    :param whitelist: specify the role type

    .. seealso::
        :class:`Role`

    :returns: New :class:`Role` type
    """

    BaseKlass = role_base or Role
    return BaseKlass(
        whitelist=whitelist,
        *fields,
        **kwargs
    )


def whitelist(*fields, **kwargs):
    """Helper function that explicitly creates a new :class`Role` type
    setting the whitelist option to True

    :param fields: iterable of field names
    :param role_base: specify a custom role type to create a role from

    e.g::
        role=whitelist('name', 'email')

    .. seealso::
        :func:`_create_role`

    :returns: New :class:`Role` type
    """
    role_base = kwargs.pop('role_base', None)
    return _create_role(fields,
                        role_base=role_base,
                        whitelist=True,
                        **kwargs)


def blacklist(*fields, **kwargs):
    """Helper function that explicitly creates a new :class`Role` type
    setting the whitelist option to False

    :param name: the name given to this role
    :param fields: iterable of field names
    :param role_base: specify a custom role type to create a role from

    e.g::
        role=blacklist('user_public', ['name', 'email'])

    .. seealso::
        :func:`_create_role`

    :returns: New :class:`Role` type
    """
    role_base = kwargs.pop('role_base', None)
    return _create_role(fields,
                        role_base=role_base,
                        whitelist=False,
                        **kwargs)
