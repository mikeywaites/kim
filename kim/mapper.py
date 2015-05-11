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


class _MapperConfig(object):

    @classmethod
    def setup_mapping(cls, cls_, classname, dict_):
        cfg_cls = _MapperConfig
        cfg_cls(cls_, classname, dict_)

    def __init__(self, cls_, classname, dict_):

        self.dict = dict_
        self.cls = cls_
        if self.cls.__roles__ is None:
            self.cls.__roles__ = {}

        for base in reversed(self.cls.__mro__):
            self._extract_fields(base)
            self._extract_roles(base)

        if '__default__' not in self.cls.__roles__:
            self.cls.declared_roles['__default__'] = \
                list(self.cls.declared_fields.keys())

        self._remove_fields()

    def _remove_fields(self):

        for name in self.cls.declared_fields.keys():
            if getattr(self.cls, name, None):
                delattr(self.cls, name)

    def _extract_fields(self, base):

        cls = self.cls
        _fields = {}

        _fields.update(getattr(base, 'declared_fields', {}))
        for name, obj in vars(base).items():

            # Add field to declared fields and remove cls.field
            if isinstance(obj, Field):
                _fields.update({name: obj})

        cls.declared_fields = OrderedDict(
            sorted(_fields.items(), key=lambda o: o[1]._creation_order))

    def _extract_roles(self, base):

        cls = self.cls

        _roles = {}
        _roles.update(getattr(cls, 'declared_roles', None) or {})
        _roles.update(getattr(base, '__roles__', None) or {})

        cls.declared_roles = _roles


class MapperMeta(type):

    def __init__(cls, classname, bases, dict_):
        _MapperConfig.setup_mapping(cls, classname, dict_)
        type.__init__(cls, classname, bases, dict_)


class Mapper(with_metaclass(MapperMeta, object)):
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
