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
        result = super(Role, self).__or__(other)
        return Role(*[k for k in result])


class whitelist(Role):

    def __init__(self, *args, **kwargs):
        self.whitelist = True
        kwargs['whitelist'] = True
        super(whitelist, self).__init__(*args, **kwargs)


class blacklist(Role):

    def __init__(self, *args, **kwargs):
        kwargs['whitelist'] = False
        super(blacklist, self).__init__(*args, **kwargs)
