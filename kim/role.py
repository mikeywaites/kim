# kim/roles.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class Role(set):

    def __init__(self, *args, **kwargs):
        self.whitelist = kwargs.pop('whitelist', True)
        super(Role, self).__init__(args)

    @property
    def fields(self):

        return [k for k in self]

    def __contains__(self, key):
        if self.whitelist:
            return super(Role, self).__contains__(key)
        else:
            return not super(Role, self).__contains__(key)

    def __or__(self, other):
        """Override handling of producing the union of two Roles to provide
        native support for merging whitelist and blacklist roles correctly.

        This overloading allows users to produce the union of two roles that
        may, on one side, want to allow fields and on the other exclude them.

        .. codeblock:: python

            >>>from kim.role import whitelist, blacklist
            >>>my_role = whitelist('foo', 'bar') | blacklist('foo', 'baz')
            >>>my_role
            Role('bar')

        :param other: another instance of :py:class:``.Role``
        :raises: :py:class:`.RoleError``

        :rtype: :py:class:``.Role``
        :returns: a new :py:class:``.Role`` containng the set of field names

        """
        if not isinstance(other, Role):
            raise RoleError('union of built types is '
                            'not supported with roles')

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
            result = other - self

        else:  # both roles are blacklist, union them and set whitelist=False
            whitelist = False
            result = super(Role, self).__or__(other)

        return Role(*[k for k in result], whitelist=whitelist)


class whitelist(Role):

    def __init__(self, *args, **kwargs):
        self.whitelist = True
        kwargs['whitelist'] = True
        super(whitelist, self).__init__(*args, **kwargs)


class blacklist(Role):

    def __init__(self, *args, **kwargs):
        kwargs['whitelist'] = False
        super(blacklist, self).__init__(*args, **kwargs)
