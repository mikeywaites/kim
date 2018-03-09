# kim/roles.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from kim.exception import RoleError


class Role(set):
    """Roles are a fundamental feature of Kim.  It's very common to need
    to provide a different view of your data or to only require a selection of
    fields when marshaling data.  ``Roles`` in Kim allow users
    to shape their data at runtime in a simple yet flexible manner.

    ``Roles`` are added to your :py:class:`~.Mapper` declarations
    using the ``__roles__`` attribute.

    Usage::

        from kim import Mapper, whitelist, field

        class UserMapper(Mapper):
            __type__ = User

            id = field.Integer(read_only=True)
            name = field.String(required=True)
            company = field.Nested('myapp.mappers.CompanyMapper')

            __roles__ = {
                'id_only': whitelist('id')
            }

    """

    def __init__(self, *args, **kwargs):
        """initialise a new :class:`Role`.

        :param whitelist:  pass a boolean indicating whether this
            role is a whitelist

        """
        self.whitelist = kwargs.pop('whitelist', True)
        self.nested_roles = kwargs.pop('nested_roles', [])
        super(Role, self).__init__(args)

    @property
    def fields(self):
        """return an iterable containing all the field names defined in this
        role.

        :rtype: list
        :returns: iterable of field names
        """

        return [k for k in self]

    def __contains__(self, field_name):
        """overloaded membership test that inverts the check depending on
        wether the role is a whitelist or blacklist.

        If the role is defined as whitelist=True the normal membership test
        is applied ie::

            >>> 'name' in whitelist('name')
            True

        For blacklist the test is flipped as we are aiming to ensure the field
        name is not present in the role::

            >>> 'other_name' in blacklist('name')
            True
            >>> 'name' in blacklist('name')
            False

        :param field_name: name of a field to test for membership
        :rtype: boolean
        :returns: boolean indicating wether field_name is found in the role
        """
        if self.whitelist:
            return super(Role, self).__contains__(field_name)
        else:
            return not super(Role, self).__contains__(field_name)

    def __or__(self, other):
        """Override handling of producing the union of two Roles to provide
        native support for merging whitelist and blacklist roles correctly.

        This overloading allows users to produce the union of two roles that
        may, on one side, want to allow fields and on the other exclude them.

        Usage::

            >>> from kim.role import whitelist, blacklist
            >>> my_role = whitelist('foo', 'bar') | blacklist('foo', 'baz')
            >>> my_role
            Role('bar')

        :param other: another instance of :class:`kim.role.Role`
        :raises: :class:`kim.exception.RoleError`
        :rtype: :class:`kim.role.Role`
        :returns: a new :class:`kim.role.Role` containng the set of field names

        """
        if not isinstance(other, Role):
            raise RoleError('union of built in types is not supported with roles')

        whitelist = True

        if self.whitelist and other.whitelist:
            # both roles are whitelists, return the union of both sets
            result = super(Role, self).__or__(other)

        elif self.whitelist and not other.whitelist:
            # we need to remove the fields in self(whitelist)
            # that appear in other(blacklist)
            result = super(Role, self).__sub__(other)

        elif not self.whitelist and other.whitelist:
            # Same as above, except we are keeping the fields from other
            result = other.__sub__(self)

        else:
            # both roles are blacklist, union them and set whitelist=False
            whitelist = False
            result = super(Role, self).__or__(other)

        return Role(*[k for k in result], whitelist=whitelist)

    def __and__(self, other):
        """Override handling of producing the intersection of two Roles to provide
        native support for merging whitelist and blacklist roles correctly.

        This overloading allows users to produce the intersection of two roles that
        may, on one side, want to allow fields and on the other exclude them.

        .. codeblock:: python

            >>>from kim.role import whitelist, blacklist
            >>>my_role = whitelist('foo', 'bar') & blacklist('foo', 'baz')
            >>>my_role
            Role('bar')

        :param other: another instance of :py:class:``.Role``
        :raises: :py:class:`.RoleError``

        :rtype: :py:class:``.Role``
        :returns: a new :py:class:``.Role`` containng the set of field names

        """
        if not isinstance(other, Role):
            raise RoleError('intersection of built types is '
                            'not supported with roles')

        whitelist = True

        if self.whitelist and other.whitelist:
            # both roles are whitelists, return the union of both sets
            result = super(Role, self).__and__(other)

        elif self.whitelist and not other.whitelist:
            # we need to remove the fields in self(whitelist)
            # that appear in other(blacklist)
            result = super(Role, self).__sub__(other)

        elif not self.whitelist and other.whitelist:
            # Same as above, except we are keeping the fields from other
            result = other.__sub__(self)

        else:  # both roles are blacklist, union them and set whitelist=False
            whitelist = False
            result = super(Role, self).__or__(other)

        return Role(*[k for k in result], whitelist=whitelist)


class whitelist(Role):
    """ Whitelists are roles that define a list of fields that are
    permitted for inclusion when marhsaling or serializing.
    For example, a whitelist role called ``id_only`` that contains
    the field name ``id`` instructs kim that whenever
    the ``id_only`` role is used **only** the ``id`` field should be
    considered in the input/output data.

    Usage::

        from kim import whitelist

        id_only_role = whitelist('id')

        class IdMixin(object):

            id = fields.Integer(read_only=True)

            __roles__ = {
                'id_only': id_only
            }
    """

    def __init__(self, *args, **kwargs):
        self.whitelist = True
        kwargs['whitelist'] = True
        super(whitelist, self).__init__(*args, **kwargs)


class blacklist(Role):
    """ Blacklists are role that act in the opposite manner to whitelists.
    They define a list of fields that should not be used
    when marshaling and serializing data.  A blacklist role named ``id_less``
    that contained the field name ``id`` would instruct kim that every
    field defined on the mapper should be considered except ``id``.

    Usage::

        from kim import whitelist

        class UserMapper(Mapper):

            id_less_role = blacklist('id')

            __roles__ = {
                'id_less': blacklist('id')
            }
    """

    def __init__(self, *args, **kwargs):
        kwargs['whitelist'] = False
        super(blacklist, self).__init__(*args, **kwargs)


class nested_role(object):
    """Nested roles allow you to specify the role of a :class:.`kim.field.Nested` field
    on a mapper to be used when serializing or marshaling a Mapper
    conataining a Nested field.

    Example::

        class UserMapper(Mapper):
            __type__ = User

            id = field.Integer()
            name = field.String()
            email = field.Email()

            __roles__ = {
                'public': whitelist('id', 'name')
            }


        class Post(Mapper):
            __type__ = Post

            id = field.Integer()
            created_by = field.Nested('UserMapper')
            text = field.String()
            likes = field.Collection(field.Nested('UserMapper'))

            __roles__ = {
                'list': whitelist('id', 'name', nested_role('created_by', role='public'))
            }


        mapper = PostMapper(obj=posts)
        mapper.serialize(role='list')


    When the PostMapper is serialized using the list role, the Nested role will instruct
    Kim that when it processes the Nested created_by field, it should use the public Role.

    the nested role also support membership tests on the main Role object.

    .. code-block::

        role = whitelist('id', 'name', nested_role('user', role='public'))
        assert 'user' in role

    .. versionadded:: 1.3.0
    """

    def __init__(
            self, name,
            role='__default__',
            serialize_role=None,
            marshal_role=None,
            *args, **kwargs):
        """Construct a new nested_role instance.  The nested_role implicitly acts
        as a :class:`kim.role.whitelist`.

        :param name: The name of the nested field this nested_role is referring to.
        :param role: The name of the role to use for both Marshaling and Serializing the
            nested field.
        :param serialize: The name of a role to use when serializing the nested field.
        :param marshal: The name of a role to use when marshaling the nested field
        """

        self.name = name
        self.role = role
        self.serialize_role = serialize_role
        self.marshal_role = marshal_role

    #     super(nested_role, self).__init__(*args, **kwargs)

    def __eq__(self, other):
        """Overload the __eq__ method so that when a Mapper asserts if a field is found
        within a role, nested_role will act as though it's name were added normally using
        the string name of the field.

        :param field_name: The name of the field the role is searching for.

        .. code-block::

            role = whitelist('id', 'name', nested_role('user', role='public'))
            assert 'user' in role

        """

        return (self.name == other.name and
                self.role == other.role and
                self.serialize_role == other.serialize_role and
                self.marshal_role == other.marshal_role)

    # def __hash__(self):
    #     """Has the nested role using the provided field name.  This means nested roles
    #     still pass membership tests on the main role object when only the nested field
    #     name is provided.

    #     .. code-block::

    #         role = whitelist('id', 'name', nested('user', role='public'))
    #         assert 'user' in role
    #     """
    #     return hash(self.name)
