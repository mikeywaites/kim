#!/usr/bin/python
# -*- coding: utf-8 -*-



class TypeABC(object):

    def __init__(self, name, source):
        self.name = name
        self.source = source


class String(TypeABC):
    pass


class Integer(TypeABC):
    pass


class Nested(TypeABC):

    def __init__(self, name='', mapped=None,
                 nullable=True, role=None, *args, **kwargs):

        self._mapping = None
        self.mapping = mapped
        self.nullable = True
        self.role = role

        super(Nested, self).__init__(name, *args, **kwargs)

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, mapped):
        from .serializers import SerializerABC
        from .mapping import MappingABC
        if isinstance(mapped, MappingABC):
            self._mapping = mapped
        elif isinstance(mapped, SerializerABC):
            self._mapping = mapped.__mapping__
        else:
            raise TypeError('Nested() must be called with a '
                            'mapping or a mapped serializer instance')

    def get_fields(self):
        if self.role:
            return self.role.get_mapping(self.mapping).fields

        return self.mapping.fields
