# kim/mapper.py
# Copyright (C) 2014-2016 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import weakref
import six
import inspect

from collections import OrderedDict, defaultdict

from .exception import MapperError, MappingInvalid
from .field import Field, FieldError, FieldInvalid
from .role import whitelist, Role
from .utils import recursive_defaultdict
from .pipelines.base import Pipe


def mapper_is_defined(mapper_name):

    return mapper_name in _MapperConfig.MAPPER_REGISTRY


def get_mapper_from_registry(mapper_or_name):
    """Serarch for a defined mapper by name inside of the mapper registry.

    User may pass either a mapper class object or the name of a defined mapper
    as a str:

        >>>mapper = get_mapper_from_registry('UserMapper')
        >>>mapper
        UserMapper

        mapper = get_mapper_from_registry(UserMapper)
        >>>mapper
        UserMapper

    :param mapper_or_name: a mapper class or name of a mapper

    :raises: MapperError
    :rtype: :py:class:`.Mapper`
    :returns: A Mapper class
    """

    from .mapper import Mapper, mapper_is_defined, _MapperConfig

    if inspect.isclass(mapper_or_name) and issubclass(mapper_or_name, Mapper):
        name = mapper_or_name.__name__
    else:
        name = mapper_or_name

    if not mapper_is_defined(name):
        raise MapperError('%s is not a valid Mapper. '
                          'Is this Mapper defined?'
                          % mapper_or_name)

    reg = _MapperConfig.MAPPER_REGISTRY
    return reg[name]


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
            self._extract_defined_pipes(base)
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

    def _extract_defined_pipes(self, base):
        """Extract, process and store pipes defined using the decorator syntax
        on this mapper

        """
        cls = self.cls
        _validators = {}
        _inputs = {}
        _processors = {}
        _outputs = {}

        for name, obj in vars(base).items():

            types = ['validation', 'process', 'output', 'input']
            hook_type = getattr(obj, '__mapper_field_hook', None)

            if not callable(obj) or hook_type not in types:
                continue
            elif hook_type == 'validation':
                for name in obj._field_names:
                    _validators.setdefault(name, [])
                    _validators[name].append(obj)
            elif hook_type == 'input':
                for name in obj._field_names:
                    _inputs.setdefault(name, [])
                    _inputs[name].append(obj)
            elif hook_type == 'process':
                for name in obj._field_names:
                    _processors.setdefault(name, [])
                    _processors[name].append(obj)
            elif hook_type == 'output':
                for name in obj._field_names:
                    _outputs.setdefault(name, [])
                    _outputs[name].append(obj)

        cls.defined_inputs = _inputs
        cls.defined_validators = _validators
        cls.defined_processors = _processors
        cls.defined_outputs = _outputs

    def _set_field_pipes(self, field, pipes, pipe_type):
        """Populate a :class:``Field`` compute chains with pipes
        extracted from mapper defenitions.

        """

        if field.name in pipes:

            for p in pipes[field.name]:
                opts = getattr(p, '__mapper_field_hook_opts', {})
                if opts['marshal']:
                    field.opts.extra_marshal_pipes[pipe_type] \
                        .append(Pipe(p, **opts['pipe_opts']))
                if opts['serialize']:
                    field.opts.extra_serialize_pipes[pipe_type] \
                        .append(Pipe(p, **opts['pipe_opts']))

            return field

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

                self._set_field_pipes(obj, cls.defined_inputs, 'input')
                self._set_field_pipes(obj, cls.defined_validators, 'validation')
                self._set_field_pipes(obj, cls.defined_processors, 'process')
                self._set_field_pipes(obj, cls.defined_outputs, 'output')

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

        # Roles may be passed as list, convert to whitelist
        # objects in this case
        for name, role in six.iteritems(_roles):
            if isinstance(role, list):
                _roles[name] = whitelist(*role)
            elif not isinstance(role, Role):
                msg = "role %s on %s must be list or Role " \
                      "instance, got %s" % (name, self.__class__.__name__,
                                            type(role))
                raise MapperError(msg)

        cls.roles = _roles


class MapperMeta(type):

    def __init__(cls, classname, bases, dict_):
        _MapperConfig.setup_mapping(cls, classname, dict_)
        type.__init__(cls, classname, bases, dict_)


class MapperSession(object):

    def __init__(self, mapper, data, output, partial=None):

        self.mapper = mapper
        self.data = data
        self.output = output
        self.partial = partial


class Mapper(six.with_metaclass(MapperMeta, object)):
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

    @classmethod
    def many(cls, **mapper_params):
        """Provide access to a :class:`.MapperIterator` to allow multiple
        items to be mapped by a mapper.

        :returns: an instance of :class`.MapperIterator`
        """

        return MapperIterator(cls, **mapper_params)

    def __init__(self, obj=None, data=None, partial=False, raw=False):
        """Initialise a Mapper with the object and/or the data to be
        serialzed/marshaled. Mappers must be instantiated once per object/data.
        At least one of obj or data must be passed.

        :param obj: the object to be serialized, or updated by marshaling
        :param data: input data to be used for marshaling
        :param raw: the mapper will instruct fields to populate themselves
            using __duner__ field names where required.
        :param partial: allow pipelines to pull data from an existing source
            or fall back to standard checks.


        :raises: :class:`.MapperError`
        :returns: None
        """

        if obj is None and data is None:
            raise MapperError(
                'At least one of obj or data must be passed to %s()'
                % self.__class__.__name__)

        self.obj = obj
        self.data = data
        self.errors = {}
        self.raw = raw
        self.partial = partial

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

    def _get_role(self, name_or_role):
        """Resolve a string to a role and check it exists, or check a
        directly passed role is a Role instance and return it.

        :param name_or_role: role name as a string or a Role instance

        :raises: :class:`.MapperError`
        :returns: Role instance
        """
        if isinstance(name_or_role, six.string_types):
            try:
                return self.roles[name_or_role]
            except KeyError:
                raise MapperError("Role '%s' not found on %s" % (
                                  name_or_role, self.__class__.__name__))
        elif isinstance(name_or_role, Role):
            return name_or_role
        else:
            raise MapperError('role must be string or Role instance, got %s'
                              % type(name_or_role))

    def _get_fields(self, name_or_role):
        """Returns a list of :class:`.Field` instances providing they are
        registered in the specified :class:`Role`.

        If the provided role_name is not found in the Mappers role list an
        error will be raised.

        :raises: MapperError
        :returns: list of :class:`.Field`
        """

        role = self._get_role(name_or_role)
        return [f for name, f in six.iteritems(self.fields) if name in role]

    def _data_supports_transform(self, data):
        """return a boolean indicating if the given data object supports key
        based iteration

        :param data: the data object being used for iteration

        """

        return getattr(data, 'keys', False) is not False

    def _remove_none(self, output):
        """If all components of a dictionary are none, remove it and mark
        the entire data as None

        This method is used to evaluate data that has been transformed when
        the `raw=True` option is used.

        :param output: the data being evaulated

        """
        all_none = True
        for k, v in six.iteritems(output):
            if type(v) == defaultdict:
                output[k] = self._remove_none(v)
            else:
                if v is not None:
                    all_none = False
        if all_none:
            return None
        else:
            return output

    def transform_data(self, data):
        """ Transform flat data from a KeyedTuple with keys in the form:
                [
                 'id',
                    'name',
                    'contact_details__phone',
                    'contact_details__address__postcode'
                    ]
                    Into:
                    {
                        'id': x,
                        'name': x,
                        'contact_details': {
                            'phone': x,
                            'address': {
                                'postcode': x
                            }
                        }
                    }
                ]

            :param data: The object or data being transformed

            :returns: transformed data

        """
        if not self._data_supports_transform(data):
            raise MapperError('%s object does not appear to '
                              'support key based iteration '
                              'required when raw=True' % type(data))

        output = recursive_defaultdict()
        for key in data.keys():
            path = key.split('__')
            target = output
            # Walk along the path until we find the final dict to insert the
            # data into
            for component in path[:-1]:
                target = target[component]
            # And finally set the key on the final dict to the relevant data
            target[path[-1]] = getattr(data, key)

        return self._remove_none(output)

    def get_mapper_session(self, data, output):
        """populate and return a new instance of :class:``MapperSession``

        :param data: data being Mapped
        :param output: obj mapper is mapping too
        """

        return MapperSession(self, data, output, partial=self.partial)

    def serialize(self, role='__default__', raw=False):
        """Serialize ``self.obj`` into a dict according to the fields
        defined on this Mapper.

        :param role: specify the role to use when serializing this mapper
        :param raw: instruct the mapper to transform the data before serializing.
            This option overrides the Mapper.raw setting.

        :raises: FieldInalid, MapperError
        :returns: dict containing serialized object
        """

        output = {}  # Should this be user definable?

        transform_data = raw or self.raw
        if transform_data:
            data = self.transform_data(self._get_obj())
        else:
            data = self._get_obj()

        for field in self._get_fields(role):
            field.serialize(self.get_mapper_session(data, output))

        return output

    def marshal(self, role='__default__'):
        """Marshal ``self.data`` into ``self.obj`` according to the fields
        defined on this Mapper.

        :returns: Object of ``__type__`` populated with data
        """

        output = self._get_obj()
        data = self.data

        fields = self._get_fields(role)

        # If this is a partial update, rather than going through all fields
        # in the role, select those fields which are actually present in
        # the data - as long as they're also present in the role.
        if self.partial:
            marshal_fields = []
            for key in data.keys():
                for field in fields:
                    if key == field.name:
                        marshal_fields.append(field)
                        break
        else:
            marshal_fields = fields

        for field in marshal_fields:
            try:
                field.marshal(self.get_mapper_session(data, output))
            except FieldInvalid as e:
                self.errors[field.name] = e.message
            except MappingInvalid as e:
                # handle errors from nested mappers.
                self.errors[field.name] = e.errors

        # Call top level mapper validator for validations involving more
        # than one field
        try:
            self.validate(output)
        except FieldInvalid as e:
            self.errors[e.field.name] = e.message
        except MappingInvalid as e:
            self.errors = e.errors

        if self.errors:
            raise MappingInvalid(self.errors)

        return output

    def validate(self, output):
        """Mappers may subclass this method to perform top-level validation
        on multiple related fields, raising `FieldInvalid` or `MappingInvalid`
        if any problems are found.

        :raises: FieldInvalid
        :raises: MappingInvalid
        """
        pass


class MapperIterator(object):
    """Provides a symetric interface for Mapping many objects in one batch.

    A simple example would be seriaizing a list of User objects from a database
    query or other source.

    .. code-block:: python
        from kim import Mapper, field

        class UserMapper(Mapper):
            __type__ = User

            id = field.Integer(read_only=True)
            name = field.String(required=True)
            company = field.Nested('myapp.mappers.CompanyMapper')

        objs = User.query.all()
        results = UserMapper.many().serialize(objs)
    """

    def __init__(self, mapper, **mapper_params):
        """Constructs a new instance of a MapperIterator.

        :param mapper: a :class:`.Mapper` to map each item too.
        :param mapper_params: a dict of kwargs passed to each mapper
        """

        self.mapper = mapper
        self.mapper_params = mapper_params

    def get_mapper(self, data=None, obj=None):
        """return a new instance of the provided mapper.

        :param data: provide the new mapper with data when marshaling
        :param obj: provide the new mapper with data when serializing

        :rtype: :class:`.Mapper`
        :returns: a new :class:`.Mapper`
        """

        self.mapper_params.update({
            'data': data,
            'obj': obj
        })
        return self.mapper(**self.mapper_params)

    def serialize(self, objs, role='__default__'):
        """Serializes each item in ``objs`` creating a new mapper each time.

        :param objs: iterable of objects to serialize
        :param role: name of a role to use when serializing

        :returns: list of serialized objects
        """

        output = []  # TODO should this be user defined?
        for obj in objs:
            output.append(self.get_mapper(obj=obj).serialize(role=role))

        return output

    def marshal(self, data, role='__default__'):
        """Marshals each item in ``data`` creating a new mapper each time.

        :param objs: iterable of objects to marshal
        :param role: name of a role to use when marshaling

        :returns: list of marshaled objects
        """

        output = []  # TODO should this be user defined?
        for datum in data:
            output.append(self.get_mapper(data=datum).marshal(role=role))

        return output
