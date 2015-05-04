# kim/mapper.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from six import with_metaclass
from collections import OrderedDict

from .exception import MapperError
from .fields import Field


class MapperMetaType(type):
    """Intercept and create new Mapper classes.
    """

    def __new__(mcs, name, bases, attrs):

        new = (super(MapperMetaType, mcs).__new__(mcs, name, bases, attrs))

        # Traverse the MRO collecting fields from base classes.
        fields = {}
        for base in new.__mro__:

            for name, obj in vars(base).items():

                if name == 'declared_fields':
                    fields.update(obj)

        for name, obj in attrs.items():
            if isinstance(obj, Field):
                fields[name] = obj

        new.declared_fields = OrderedDict(
            sorted(fields.items(), key=lambda o: o[1]._creation_order))

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

    __type__ = None
    __roles__ = None

    def get_mapper_type(self):
        """Return the spefified type for this Mapper.  If no ``__type__`` is
        defined a :class:`.MapperError` is raised

        :raises: :class:`.MapperError`
        :returns: The specified ``__type__`` for the mapper.
        """

        if self.__type__ is None:
            raise MapperError(
                '%s must define a __type__' % self.__class__.__name__)

        return self.__type__
