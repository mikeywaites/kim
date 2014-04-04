

class KimError(Exception):
    pass


class MappingError(KimError):
    pass


class ValidationError(KimError):
    pass


class RoleNotFound(KimError):
    pass
