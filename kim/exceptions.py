

class KimError(Exception):
    pass


class MappingError(KimError):
    pass


#TODO REMOVE THIS
class ValidationError(KimError):
    pass


class ValidationErrors(KimError):
    pass


class RoleNotFound(KimError):
    pass


class ConfigurationError(KimError):
    pass


class FieldError(KimError):
    pass
