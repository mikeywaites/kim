from collections import OrderedDict
from .mapping import Mapping
from .types import TypeABC, String


def with_metaclass(meta, *bases):
    '''Defines a metaclass.

    Creates a dummy class with a dummy metaclass. When subclassed, the dummy
    metaclass is used, which has a constructor that instantiates a
    new class from the original parent. This ensures that the dummy class and
    dummy metaclass are not in the inheritance tree.

    Credit to Armin Ronacher.
    '''
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})


class SerializerMetaclass(type):
 def __new__(mcs, name, bases, attrs):
        # Adapted from Django forms - https://github.com/django/django/blob/master/django/forms/forms.py#L73

        # Collect fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, TypeABC):
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
        mapping = Mapping(self.__class__.__name__)
        for name, field in self.declared_fields.items():
            field.name = name
            if not field.source:
                field.source = name
            mapping.add_field(field)
        return mapping


class SerializerABC(with_metaclass(SerializerMetaclass, BaseSerializer)):
    pass


class JacksSerializer(SerializerABC):
    bla = String()
    lol = String(source='something')


mapping = JacksSerializer().get_mapping()
import ipdb; ipdb.set_trace()