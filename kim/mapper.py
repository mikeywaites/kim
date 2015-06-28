# kim/mapper.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import weakref

from six import with_metaclass, iteritems
from collections import OrderedDict

from .exception import MapperError
from .field import Field, FieldError
from .role import whitelist


def add_class_to_registry(classname, cls):
    """Register ``cls`` inside if the registry using ``classname``.  If a cls
    for this name already exists inside the registry an error will be raised.

    :param classname: the name of the class used as the key inside the registry
    :param cls: the class being stored

    :raises :class:`kim.exception.MapperError`
    :returns: None
    """

    if classname in _MapperConfig.MAPPER_REGISTRY:
        msg = '%s is already a registered Mapper' % classname
        raise MapperError(msg)
    else:
        _MapperConfig.MAPPER_REGISTRY[classname] = cls


class _MapperConfig(object):

    MAPPER_REGISTRY = weakref.WeakValueDictionary()

    @classmethod
    def setup_mapping(cls, cls_, classname, dict_):
        cfg_cls = _MapperConfig
        cfg_cls(cls_, classname, dict_)

    def __init__(self, cls_, classname, dict_):

        self.dict = dict_
        self.cls = cls_

        for base in reversed(self.cls.__mro__):
            self._extract_fields(base)
            self._extract_roles(base)

        # If a __default__ role is found in the cls.__roles__ property, assume
        # the user is looking to override the default role and dont create one
        # here.
        if '__default__' not in self.cls.__roles__:
            self.cls.roles['__default__'] = \
                whitelist(*self.cls.fields.keys())

        self._remove_fields()
        add_class_to_registry(classname, self.cls)

    def _remove_fields(self):
        """Cycle through the list of ``fields`` and remove those
        fields as attrs from the new cls being generated

        :returns: None
        """

        for name in self.cls.fields.keys():
            if getattr(self.cls, name, None):
                delattr(self.cls, name)

    def _extract_fields(self, base):
        """Cycle over attrs declared on ``base`` searching for a types that
        inherit from :class:`kim.field.Field`.  If a field type is found, store
        it inside ``fields``.

        :param base: Current class from the MRO.
        :returns: None
        """

        cls = self.cls
        _fields = {}

        _fields.update(getattr(base, 'fields', {}))
        for name, obj in vars(base).items():

            # Add field to declared fields and remove cls.field
            if isinstance(obj, Field):
                try:
                    obj.name
                except FieldError:
                    obj.name = name
                _fields.update({name: obj})

        cls.fields = OrderedDict(
            sorted(_fields.items(), key=lambda o: o[1]._creation_order))

    def _extract_roles(self, base):
        """update ``roles`` with any roles defined previously in
        the MRO and add any roles defined on the current
        ``base`` being iterated.

        Each base iterated in the MRO overwrites ``roles`` allowing
        users to inherit and override roles all the way up the inheritance
        chain.

        :param base: Current class from the MRO.
        :returns: None
        """

        cls = self.cls

        _roles = {}
        _roles.update(getattr(cls, 'roles', None) or {})
        _roles.update(getattr(base, '__roles__', None) or {})

        cls.roles = _roles


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
        from kim import Mapper, field

        class UserMapper(Mapper):
            __type__ = User

            id = field.Integer(read_only=True)
            name = field.String(required=True)
            company = field.Nested('myapp.mappers.CompanyMapper')

    """

    __type__ = None
    __roles__ = {}

    def __init__(self, obj=None, data=None):
        """Initialise a Mapper with the object and/or the data to be
        serialzed/marshaled. Mappers must be instantiated once per object/data.
        At least one of obj or data must be passed.

        :param obj: the object to be serialized, or updated by marshaling
        :param data: input data to be used for marshaling
        :raises: :class:`.MapperError`
        :returns: None
        """

        if obj is None and data is None:
            raise MapperError(
                'At least one of obj or data must be passed to %s()'
                % self.__class__.__name__)

        self.obj = obj
        self.data = data

    def _get_mapper_type(self):
        """Return the spefified type for this Mapper.  If no ``__type__`` is
        defined a :class:`.MapperError` is raised

        :raises: :class:`.MapperError`
        :returns: The specified ``__type__`` for the mapper.
        """

        if self.__type__ is None:
            raise MapperError(
                '%s must define a __type__' % self.__class__.__name__)

        return self.__type__

    def _get_obj(self):
        """Return ``self.obj`` or create a new instance of ``self.__type__``

        :returns: ``self.obj`` or new instance of ``self.__type__``
        """
        if self.obj is not None:
            return self.obj
        else:
            return self._get_mapper_type()()

    def serialize(self):
        """Serialize ``self.obj`` into a dict according to the fields
        defined on this Mapper.

        :returns: dict containing serialized object
        """

        output = {}  # Should this be user definable?

        for _, field in iteritems(self.fields):
            field.serialize(self.obj, output)

        return output

    def marshal(self):
        """Marshal ``self.data`` into ``self.obj`` according to the fields
        defined on this Mapper.

        :returns: Object of ``__type__`` populated with data
        """

        output = self._get_obj()

        for _, field in iteritems(self.fields):
            field.marshal(self.data, output)

        return output
