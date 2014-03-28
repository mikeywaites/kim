#!/usr/bin/python
# -*- coding: utf-8 -*-


from .exceptions import ValidationError


class Validator(object):

    error_message = u'Generic Field Error'

    def validate(self, field_type, value):
        """the validate method of the Validator object, as the name suggests,
        performs validation for a field and a source value.

        Concrete classes must implement this method themselves.  The validate
        method should return a bool indicating wether the validation was
        succesful or not.

        :param field_type: :class:`kim.types.BaseType` instance from a mapping
        :param value: the value being validated for this Type

        :raises: NotImplementedError
        :rtype: boolean
        :returns: boolean True for success, False otherwise
        """
        raise NotImplementedError('Validator() types must implement '
                                  'the validate method')

    def run(self, field_type, value):
        """ :meth:`run` is called when marshalling mapped types from
        user input.  Typically this method will not be overridden by
        concrete classes, instead see :meth:`validate`

        :param field_type: :class:`kim.types.BaseType` instance from a mapping
        :param value: the value being validated for this Type

        :raises: ValidationError
        :returns: None

        .. seealso::
            :meth:`get_error`
        """

        if not self.validate(field_type, value):
            raise ValidationError(self.get_error())

    def get_error(self, field_type, value):
        """Return a humand readable error message for this validator
        when validation fails.

        :param field_type: :class:`kim.types.BaseType` instance from a mapping
        :param value: the value being validated for this Type

        :type: mixed
        :returns: Error message describing the validation error.
        """

        return self.error_message


class TypedValidator(Validator):

    def __init__(self, type_, *args, **kwargs):
        super(TypedValidator, self).__init__(*args, **kwargs)
        self.type_ = type_

    def validate(self, field_type, value):

        if not isinstance(value, self.type_):
            return False

        return True
