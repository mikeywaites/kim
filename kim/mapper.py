# kim/mapper.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from six import with_metaclass
from collections import OrderedDict

from .fields import Field


class MapperMetaType(type):
    """Intercept new and create new Mapper classes.
    """

    def __new__(mcs, name, bases, attrs):

        _fields = []
        for attr_name, attr in list(attrs.items()):

            # collect all declared field attributes.
            if isinstance(attr, Field):
                _fields.append((attr_name, attr))
                attrs.pop(attr_name)

        new = (super(MapperMetaType, mcs).__new__(mcs, name, bases, attrs))

        # Traverse the MRO collecting fields from base classes.
        declared_fields = OrderedDict(_fields)
        for base in reversed(new.__mro__):
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

        new.declared_fields = declared_fields
        return new


class Mapper(with_metaclass(MapperMetaType, object)):
    """Mappers are the building blocks of Kim - they define how JSON output
    should look and how input JSON should be expected to look.

    Mappers consist of Fields. Fields define the shape and nature of the data
    both when being serialised(output) and marshaled(input).

    Mappers must define a __type__. This is the type that will be
    instantiated if a new object is marshaled through the mapper. __type__
    maybe be any object that supports setter and getter functionality.

    .. code-block:: python
        from kim import Mapper, fields

        class UserMapper(Mapper):
            __type__ = User

            id = fields.Integer(read_only=True)
            name = fields.String(required=True)
            company = fields.Nested('myapp.mappers.CompanyMapper')

    """

    def marshal(self, data, role=None):
        pass

    def serialize(self, data, role=None):
        pass
