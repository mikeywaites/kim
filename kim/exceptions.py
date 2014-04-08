

class KimError(Exception):
    pass


class ValidationError(KimError):
    """Exception used by Types to raise an error when their validate
    method fails

    ..seealso::
        :meth:`kim.types.BaseType.validate`

    """
    pass


class FieldError(ValidationError):
    """A type of :class:`.ValidationError` that also accepts the field
    name specified as `key`

    """

    def __init__(self, key, *args, **kwargs):
        super(FieldError, self).__init__(*args, **kwargs)

        self.key = key


class MappingErrors(KimError):
    pass


class RoleNotFound(KimError):
    pass


class ConfigurationError(KimError):
    pass
