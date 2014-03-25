#!/usr/bin/python
# -*- coding: utf-8 -*-

from .exceptions import FieldError
from .validators import validate, TypeValidator


class BaseField(object):

    field_default = None

    def __init__(self, default=None, validators=None, attribute=None):

        self._value = default or self.field_default
        self.validators = validators or []
        self.attribute = None

    @property
    def value(self):
        """Get the value of the field
        """
        return self._value

    @value.setter
    def value(self, value):
        """Setter for field.value.  When set operation is called
        the value will be passed though the defined, if any, validators
        specified in `self.validators`

        :param value: the field value being set
        """
        validate(value, self.validators)
        self._value = value


class TypedBaseField(BaseField):
    """A typed field interface that adds :class:`TypedValidator`
    to `validators`.

    Implementing classes must specify the _type attribute or a
    :class:`kim.exceptions.FieldError` error will be raised::

        class String(TypedBaseField):
            _type = str

    .. seealso::
        :meth:`kim.validators.TypeValidator`

    """

    field_type = None

    def __init__(self, default=None, validators=None, *args, **kwargs):

        if self.field_type is None:
            raise FieldError('{0}.field_type must not be '
                             'none for a TypedBaseField'.format(
                                 self.__class__.__name__))

        validators = validators or list()
        validators.append(TypeValidator(self._type))
        super(TypedBaseField, self).__init__(default=default,
                                             validators=validators,
                                             *args,
                                             **kwargs)


class String(TypedBaseField):

    _type = basestring
    field_default = basestring()
