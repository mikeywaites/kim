# kim/roles.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class Role(set):

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(args, **kwargs)

    @property
    def fields(self):

        return [k for k in self]

    def __or__(self, other):
        result = super(Role, self).__or__(other)
        return Role(*[k for k in result])
