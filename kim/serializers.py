from inspect import isclass
from collections import OrderedDict
import json

from .mapping import Mapping, serialize
from .types import TypeMapper, CollectionTypeMapper


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
    mapped_type_cls = TypeMapper

    def __init__(self, field_type, name=None, source=None):
        if isclass(field_type):
            field_type = field_type()
        self.field_type = field_type
        self.name = name
        self.source = source

    def get_mapped_type(self, name):
        name = self.name or name
        source = self.source or name
        return self.mapped_type_cls(name, self.field_type, source=source)


class Collection(Field):
    mapped_type_cls = CollectionTypeMapper


class SerializerMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        # Adapted from Django forms -
        # https://github.com/django/django/blob/master/django/forms/forms.py#L73

        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                current_fields.append((key, value))
                attrs.pop(key)

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
        mapping = Mapping(name)

        for name, field_wrapper in new_class.declared_fields.items():
            mapping.add_field(field_wrapper.get_mapped_type(name))

        return mapping


class BaseSerializer(object):
    pass


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
