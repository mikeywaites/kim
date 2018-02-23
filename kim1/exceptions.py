

class KimError(Exception):
    pass


class ValidationError(KimError):
    """Exception used by Types to raise an error when their validate
    method fails

    ..seealso::
        :meth:`kim.types.BaseType.validate`

    """
    def __init__(self, message=None, *args, **kwargs):
        super(ValidationError, self).__init__(*args, **kwargs)

        self.message = message


class FieldError(ValidationError):
    """A type of :class:`.ValidationError` that also accepts the field
    name specified as `key`

    """

    def __init__(self, key, *args, **kwargs):
        super(FieldError, self).__init__(*args, **kwargs)

        self.key = key


class MappingErrors(KimError):

    def __init__(self, message=None, *args, **kwargs):
        super(MappingErrors, self).__init__(*args, **kwargs)

        self.message = message


class ConfigurationError(KimError):
    pass


class RoleNotFound(KimError):
    pass
