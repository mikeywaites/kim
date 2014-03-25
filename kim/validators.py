
from .exceptions import ValidatorTypeError, ValidationError


def validate(value, validators):
    """utility function that accepts a list of validation interfaces
    and runs the validate method::

        vals = [TypeValidator, EmailValidator]
        validate("hello@foo.com", vals)

    :param value: the value being validated
    :param validators: an iterable of validator types

    :raises: :class:`.exceptions.ValidatorTypeError`
             :class:`.exceptions.ValidationError`

    :returns: None
    """

    for v in validators:
        try:
            v.validate(value)
        except AttributeError:
            raise ValidatorTypeError("validators must implement the "
                                     "validate method")
        except ValidationError:
            raise


class BaseValidator(object):

    def validate(self, value, *args, **kwargs):
        raise NotImplementedError("Validators must implement the "
                                  "validate method")


class TypeValidator(BaseValidator):

    def __init__(self, type_, *args, **kwargs):
        self.type_ = type_

    def validate(self, value, *args, **kwargs):

        if not type(value) == self.type_:
            raise ValidationError("value is not of the right type")

        return value
