from collections import OrderedDict
from .mapping import Mapping
from .util import with_metaclass


class Field(object):
    """Wrapper representing a :class:`kim.types.Type` in a
    :class:`kim.serializers.Serializer`.

    :param field_type: The `Type` class to use for this `Field` (note this should
        be a class, not an instantiated object)
    :param **params: Extra params to be passed to the `Type` constructor, eg.
        `source`

    .. seealso::

    :class:`kim.serializers.Serializer`
    """

    def __init__(self, field_type, **params):
        self.field_type = field_type
        self.params = params


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

            # Field shadowing.
            for attr in base.__dict__.keys():
                if attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class BaseSerializer(object):
    def get_mapping(self):
        """Return a :class:`kim.mapping.Mapping` built up from the
        attributes on this Serializer."""
        mapping = Mapping(self.__class__.__name__)
        for name, field_wrapper in self.declared_fields.items():
            params = field_wrapper.params
            params.setdefault('source', name)
            field = field_wrapper.field_type(name=name, **params)
            mapping.add_field(field)
        return mapping


class Serializer(with_metaclass(SerializerMetaclass, BaseSerializer)):
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
