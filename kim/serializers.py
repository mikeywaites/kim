from inspect import isclass
from collections import OrderedDict
import json

from .exceptions import RoleNotFound, ConfigurationError
from .mapping import Mapping, serialize, marshal
from .type_mapper import TypeMapper
from .utils import is_role
from .types import BaseType


class Field(object):
    """Wrapper representing a :class:`kim.types.Type` in a
    :class:`kim.serializers.Serializer`.

    :param field_type: The `Type` to use for this `Field` (note this should
        be an instantiated object)
    :param **params: Extra params to be passed to the `Type` constructor, eg.
        `source`

    .. seealso::
        :class:`kim.serializers.Serializer`
    """

    def __init__(self, field_type, name=None, source=None):
        if isclass(field_type):
            field_type = field_type()
        self.field_type = field_type
        self.name = name
        self.source = source

    def get_mapped_type(self, name):
        name = self.name or name
        source = self.source or name
        return TypeMapper(name, self.field_type, source=source)


class SerializerMetaclass(type):

    def __new__(mcs, name, bases, attrs):

        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                current_fields.append((key, value))
                attrs.pop(key)
            elif isinstance(value, BaseType):
                # Handle common mistake of failing to wrap types in Field()
                # where passed as instance
                type_name = value.__class__.__name__
                raise ConfigurationError('Serializer attributes must be wrapped ' \
                    'in Field. Raw type %s found on %s. Did you mean Field(%s())?' %
                    (type_name, name, type_name))
            elif isclass(value) and issubclass(value, BaseType):
                # Handle common mistake of failing to wrap types in Field()
                # where passed as class
                type_name = value.__name__
                raise ConfigurationError('Serializer attributes must be wrapped ' \
                    'in Field. Raw type %s found on %s. Did you mean Field(%s)?' %
                    (type_name, name, type_name))


        attrs['declared_fields'] = OrderedDict(current_fields)

        new_class = (super(SerializerMetaclass, mcs)
                     .__new__(mcs, name, bases, attrs))

        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        new_class.__mapping__ = mcs.build_mapping(name, new_class)

        return new_class

    @staticmethod
    def build_mapping(name, new_class):
        mapping = Mapping()
        for name, field_wrapper in new_class.declared_fields.items():
            mapping.add_field(field_wrapper.get_mapped_type(name))

        return mapping


class SerializerOpts(object):

    def __init__(self, meta):

        self.roles = getattr(meta, 'roles', {})


class BaseSerializer(object):

    class Meta:
        """meta class for providing extra options for a serializer

        Options::

            Roles may be assigned to a serializer using the roles
            meta option.  roles should be specified as a dict of
            role name: Role() instance.

            roles = {'public': whitelist('field_a', 'field_b')}

            .. seealso::
                :class:`kim.roles.Role`

        """


class Serializer(BaseSerializer):
    """:class:`kim.serializer.Serializer` is a declarative wrapper for
    generating :class:`kim.mapping.Mapping`s. It also provides convinience
    methods for marshalling data against it's mapping.

    Whilst it is not nessasary to use a :class:`kim.serializer.Serializer` to
    use Kim, it is recommended for most users as the default way to
    interact with the low level :class:`kim.mapping.Mapping` API.

    Serializers consist of attributes representing fields. These will become
    keys in the resulting serialized data. If the Field does not list a source,
    the source will default to the field name.

    e.g.::
        class MySerializer(Serializer):
            name = Field(String)
            age = Field(Interger, source='user_age')


    .. seealso::

        :class:`kim.serializers.Field`

    """

    __metaclass__ = SerializerMetaclass

    def __init__(self, data=None, input=None):
        self.source_data = data
        self.input = input
        self.opts = SerializerOpts(self.Meta)

    def get_role(self, role):
        """Find and return a serializer role.  `role` may be provided to
        :meth:`serialize` or :meth:`marshal` as a role instance or as
        a string representing a role name defined in `self.opts.roles`

        :raises: RoleNotFound
        :returns: an instance of a role
        """
        if is_role(role):
            return role

        try:
            return self.opts.roles[role]
        except KeyError:
            raise RoleNotFound('Missing role %s' % role)

    def get_mapping(self, role=None):
        """return the serializers mapping.  If `role` is supplied
        then the mapping will be returned via :meth:`get_mapping` method
        on the `role` instance.

        :param role: name of role or role instance.

        :returns: mapping or mapping for a role
        """
        if role:
            role = self.get_role(role)
            return role.get_mapping(self.__mapping__)

        return self.__mapping__

    def serialize(self, role=None, **kwargs):
        return serialize(self.get_mapping(role=role), self.source_data, **kwargs)

    def json(self):
        return json.dumps(self.serialize())

    def marshal(self, role=None, **kwargs):
        return marshal(self.get_mapping(role=role), self.input, **kwargs)
